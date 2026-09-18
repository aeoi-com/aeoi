// Load test of the browser app with a large institution: N accounts (default 3'000) through the
// whole flow - validate the XML, check the workbook, plan against a registry, build + encrypt,
// record the outcome, plan and build the correction, restore the registry from the files.
// Every step is timed inside the real browser (Pyodide on the main thread) and must finish
// within its budget; the page must not throw. Same setup as web_browser_test.mjs:
//   PW_CHANNEL=chrome node tools/web_load_test.mjs        (AEOI_LOAD_N=1000 for a smaller run)
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { mkdirSync, readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const scratch = process.env.PYODIDE_DIR || join(root, ".local", "pyodide-test");
process.env.PLAYWRIGHT_BROWSERS_PATH ||= join(scratch, "browsers");
const { chromium } = createRequire(join(scratch, "package.json"))("playwright");
const N = Number(process.env.AEOI_LOAD_N || 3000);
const fixtures = join(scratch, "load");
mkdirSync(fixtures, { recursive: true });
const py = process.env.AEOI_PYTHON || join(root, ".venv", "Scripts", "python.exe");
const fx = fixtures.replace(/\\/g, "/");

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: ["ignore", "inherit", "inherit"] });
    p.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`))));
  });
}
const checks = [];
function check(name, cond) {
  checks.push([name, !!cond]);
  console.log((cond ? "ok   " : "FAIL ") + name);
}
const sec = (ms) => (ms / 1000).toFixed(1) + " s";
const mb = (n) => (n / 1048576).toFixed(1) + " MB";

// ---- fixtures: N accounts (2/3 persons with a payment, 1/3 entities with a controlling person),
// the changed workbook (10 % of the balances), the XML of the first, a test key pair ----
await run(py, ["-c", `
import datetime as dt, random
from decimal import Decimal
from aeoi.crs import build, template
from aeoi.crs.example import sample_message
from aeoi.crs.model import Account, Address, ControllingPerson, Organisation, Payment, Person, Tin
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
rnd = random.Random(7)
countries = ["DE", "FR", "IT", "AT", "GB", "ES", "NL", "BE", "SE", "PT"]
first = ["Anna", "Luca", "Marie", "Jonas", "Sofia", "Paul", "Elena", "Max", "Laura", "Noah"]
last = ["Müller", "Rossi", "Dupont", "Schmid", "Bernard", "Weber", "Ferrari", "Meier", "Martin", "Keller"]
def person(i, cc):
    return Person(first_name=first[i % 10], last_name=f"{last[(i // 10) % 10]} {i}", birth_date=dt.date(1950 + i % 50, 1 + i % 12, 1 + i % 28),
                  residence_countries=[cc], tins=[Tin(value=f"{cc}{i:09d}", issued_by=cc)],
                  address=Address(country=cc, street="Hauptstrasse", building_identifier=str(1 + i % 200), post_code=f"{10000 + i % 89999}", city="Stadt"))
def iban(i):  # a valid Swiss IBAN (60000 checks the mod-97 checksum)
    bban = f"{i:017d}"
    digits = "".join(str(int(c, 36)) for c in bban + "CH00")
    return f"CH{98 - int(digits) % 97:02d}{bban}"
def account(i):
    cc = countries[i % len(countries)]
    number = iban(i)
    if i % 3:
        return Account(key=f"A{i}", account_number=number, account_number_type="OECD601", holder_person=person(i, cc),
                       balance=Decimal(rnd.randint(0, 5_000_000)) / 100, currency="CHF",
                       payments=[Payment(payment_type="CRS502", amount=Decimal(rnd.randint(0, 100_000)) / 100, currency="CHF")],
                       self_cert="CRS901", dd_procedure="CRS1202", account_type="CRS1101")
    return Account(key=f"A{i}", account_number=number, account_number_type="OECD605",
                   holder_organisation=Organisation(name=f"Holding {i} SA", acct_holder_type="CRS101", residence_countries=[cc], ins=[Tin(value=f"{cc}IN{i}", issued_by=cc)],
                                                    address=Address(country=cc, street="Rue Neuve", building_identifier="1", post_code="75001", city="Ville")),
                   controlling_persons=[ControllingPerson(person=person(i + 1, cc), ctrlg_person_types=["CRS801"], self_cert="CRS1001")],
                   balance=Decimal(rnd.randint(0, 50_000_000)) / 100, currency="EUR",
                   self_cert="CRS902", dd_procedure="CRS1201", account_type="CRS1104", equity_interest_types=["CRS401"])
msg = sample_message()
msg.accounts = [account(i) for i in range(1, ${N} + 1)]
template.write_message(msg, "${fx}/LOAD.xlsx")
open("${fx}/Test-LOAD.xml", "w", encoding="utf-8").write(build.build(msg, "3.0", test=True).xml)
for a in msg.accounts[::10]:
    a.balance += 1
template.write_message(msg, "${fx}/LOAD-changed.xlsx")
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
open("${fx}/ESTV-PublicKey.pem", "wb").write(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
print(f"fixtures: {len(msg.accounts)} accounts")
`]);
console.log(`LOAD.xlsx ${mb(statSync(join(fixtures, "LOAD.xlsx")).size)}, Test-LOAD.xml ${mb(statSync(join(fixtures, "Test-LOAD.xml")).size)}`);

const port = 8767;
const server = spawn(py, ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", join(root, "web")], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 1500));
const browser = await chromium.launch(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {});
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (err) => errors.push(err.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text().slice(0, 200)); });
  const cdp = await context.newCDPSession(page);
  await cdp.send("Performance.enable");
  const heap = async () => mb((await cdp.send("Performance.getMetrics")).metrics.find((m) => m.name === "JSHeapUsedSize").value);
  const consoleEvent = (prefix) => page.waitForEvent("console", { predicate: (m) => m.text().startsWith(prefix), timeout: 600000 });
  async function timed(label, budgetMs, action, waitFor) {
    const wait = waitFor ? consoleEvent(waitFor) : null;
    const t0 = performance.now();
    await action();
    const text = wait ? (await wait).text() : "";
    const ms = performance.now() - t0;
    check(`${label}: ${sec(ms)} (budget ${sec(budgetMs)})${text ? " - " + text.slice(0, 60) : ""}`, ms <= budgetMs);
    return ms;
  }
  async function withDownload(action, name) {
    const dl = page.waitForEvent("download", { timeout: 600000 });
    await action();
    const d = await dl;
    const path = join(fixtures, name || d.suggestedFilename());
    await d.saveAs(path);
    return path;
  }

  await timed("boot", 120000, () => page.goto(`http://127.0.0.1:${port}/app.html#nofsa`), "aeoi:ready");
  await timed(`validate the XML of ${N} accounts`, 120000, () => page.locator("#file").setInputFiles(join(fixtures, "Test-LOAD.xml")), "aeoi:result");
  check("XML verdict OK", (await page.locator("#out").textContent()).startsWith("OK"));
  await timed(`check the workbook of ${N} accounts (no registry)`, 120000, () => page.locator("#file").setInputFiles(join(fixtures, "LOAD.xlsx")), "aeoi:result");
  check("workbook verdict OK", (await page.locator("#out").textContent()).startsWith("OK"));
  console.log("     heap after check:", await heap());

  let regFile = await withDownload(() => page.locator("#reg-new").click(), "load-0.sqlite");
  await timed(`check + plan against the empty registry`, 120000, () => page.locator("#file").setInputFiles(join(fixtures, "LOAD.xlsx")), "aeoi:result");
  check(`plan: ${N} new`, (await page.locator("#plan .tag.new").textContent()).startsWith(String(N)));
  regFile = await withDownload(() => page.locator("#key-file").setInputFiles(join(fixtures, "ESTV-PublicKey.pem")), "load-1.sqlite");

  const built = consoleEvent("aeoi:built");
  await timed(`build + encrypt + register ${N} records`, 180000, async () => { regFile = await withDownload(() => page.locator("#build").click(), "load-2.sqlite"); await built; });
  const regSize = statSync(regFile).size;
  const pkg = await withDownload(() => page.locator(".built .btn.primary").first().click());
  const firstXml = await withDownload(() => page.locator(".built .btn:not(.primary)").first().click());
  console.log(`     registry ${mb(regSize)}, package ${mb(statSync(pkg).size)}, heap ${await heap()}`);
  check("registry under 25 MB", regSize < 25 * 1048576);

  await page.locator("#outcome-text").fill("Validierungsbestätigung: Die Meldung wurde akzeptiert.");
  await timed("record the outcome", 60000, async () => { const o = consoleEvent("aeoi:outcome"); regFile = await withDownload(() => page.locator("#outcome-record").click(), "load-3.sqlite"); await o; });

  await timed(`check + plan the changed workbook (${N / 10} changed)`, 120000, () => page.locator("#file").setInputFiles(join(fixtures, "LOAD-changed.xlsx")), "aeoi:result");
  check(`plan: ${N / 10} changed, ${N - N / 10} unchanged`, (await page.locator("#plan .tag.changed").textContent()).startsWith(String(N / 10)) && (await page.locator("#plan .tag.unchanged").textContent()).startsWith(String(N - N / 10)));
  const t0 = performance.now();
  await page.locator("#cancel-keys").fill("A2");
  await page.locator("#plan .tag.deleted").waitFor({ timeout: 120000 });
  const replan = performance.now() - t0;
  check(`re-plan after typing a cancel key: ${sec(replan)} (budget 30.0 s)`, replan <= 30000);

  const corr = consoleEvent("aeoi:built");
  await timed(`build the correction (${N / 10} OECD2 + 1 OECD3)`, 180000, async () => { regFile = await withDownload(() => page.locator("#build").click(), "load-4.sqlite"); await corr; });
  const corrXml = await withDownload(() => page.locator(".built .btn:not(.primary)").first().click());
  console.log(`     registry ${mb(statSync(regFile).size)}, heap ${await heap()}`);

  await timed("reopen the saved registry", 60000, async () => { await page.locator("#reg-file").setInputFiles(regFile); await page.locator("#reg-list tbody tr").nth(1).waitFor({ timeout: 60000 }); });
  check("registry lists 2 messages", (await page.locator("#reg-list tbody tr").count()) === 2);

  // restore: a fresh registry from the two XML files, keys from the loaded workbook
  await page.locator("#cancel-keys").fill("");
  await withDownload(() => page.locator("#reg-new").click(), "load-5.sqlite");
  const restored = consoleEvent("aeoi:restored");
  await timed(`restore the registry from the two XML files (${N} + ${N / 10 + 1} records)`, 180000, async () => { await withDownload(() => page.locator("#restore-files").setInputFiles([firstXml, corrXml]), "load-6.sqlite"); await restored; });
  check("restore: 2 files, 0 skipped", (await restored).text() === "aeoi:restored 2 0");
  console.log("     heap at the end:", await heap());
  check("no page error or console error" + (errors.length ? ": " + errors[0] : ""), errors.length === 0);
} finally {
  await browser.close();
  server.kill();
}
const failed = checks.filter(([, ok]) => !ok);
console.log(`\n${checks.length - failed.length}/${checks.length} checks passed (${N} accounts)`);
process.exit(failed.length ? 1 : 0);
