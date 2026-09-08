import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const projectRoot = path.resolve(import.meta.dirname, "../..");
const gate = path.join(projectRoot, "scripts/validate_sermon_presentation.mjs");
const fixtures = path.join(import.meta.dirname, "fixtures/sermon_presentation");

function runFixture(name, extraArgs = []) {
  const source = path.join(fixtures, name);
  const result = spawnSync(
    process.execPath,
    [gate, "--source", source, "--candidate-id", `fixture:${name}`, ...extraArgs],
    { cwd: projectRoot, encoding: "utf8" }
  );
  const output = result.stdout.trim() ? JSON.parse(result.stdout) : null;
  return { ...result, output };
}

function failedCheckIds(output) {
  return output.checks.filter((check) => check.status === "FAIL").map((check) => check.id);
}

test("PASS fixture binds source to rendered independent list blocks and mechanical ceiling", () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "ronniecross-sermon-presentation-"));
  const renderedOutput = path.join(tempDir, "pass.html");
  try {
    const result = runFixture("pass.md", ["--rendered-output", renderedOutput]);
    assert.equal(result.status, 0, result.stderr || result.stdout);
    assert.equal(result.output.status, "MECHANICAL_PRESENTATION_PASS");
    assert.equal(
      result.output.completion_ceiling,
      "incident_proven_mechanical_checks_only_not_full_reader_quality_or_aesthetic_pass"
    );
    assert.match(result.output.source.sha256, /^[a-f0-9]{64}$/);
    assert.match(result.output.rendered_html.sha256, /^[a-f0-9]{64}$/);
    assert.ok(result.output.checks.every((check) => check.status === "PASS"));

    const sections = Object.fromEntries(
      result.output.rendered_section_evidence.map((section) => [section.heading, section])
    );
    assert.equal(sections["三个重点"].renderedListItemCount, 3);
    assert.equal(sections["三个重点"].hasListBlock, true);
    assert.equal(sections["小组讨论"].renderedListItemCount, 2);
    assert.equal(sections["小组讨论"].hasListBlock, true);

    const html = fs.readFileSync(renderedOutput, "utf8");
    assert.match(html, /<ol>[\s\S]*<li>第一项：属于基督。<\/li>[\s\S]*<\/ol>/);
    assert.match(html, /<ul>[\s\S]*<li>我们如何理解“属于基督”？<\/li>[\s\S]*<\/ul>/);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test("FAIL fixture blocks slide/page production residue", () => {
  const result = runFixture("fail-production-residue.md");
  assert.equal(result.status, 1);
  assert.equal(result.output.status, "MECHANICAL_PRESENTATION_FAIL");
  assert.ok(failedCheckIds(result.output).includes("production_residue"));
});

test("FAIL fixture blocks scripture label without full-width colon", () => {
  const result = runFixture("fail-scripture-colon.md");
  assert.equal(result.status, 1);
  assert.ok(failedCheckIds(result.output).includes("scripture_label_fullwidth_colon"));
});

test("FAIL fixture blocks heading text that duplicates current ordered TOC numbering", () => {
  const result = runFixture("fail-toc-double-number.md");
  assert.equal(result.status, 1);
  assert.ok(failedCheckIds(result.output).includes("toc_heading_duplicate_numbering_risk"));
});

test("FAIL fixture proves plain source newlines do not establish itemized rendered blocks", () => {
  const result = runFixture("fail-source-newline-blocks.md");
  assert.equal(result.status, 1);
  assert.ok(failedCheckIds(result.output).includes("itemized_section_source_structure"));
  const section = result.output.rendered_section_evidence.find(
    (entry) => entry.heading === "三个重点"
  );
  assert.equal(section.sourceListItemCount, 0);
  assert.equal(section.hasListBlock, false);
  assert.equal(section.renderedListItemCount, 0);
});

test("FAIL fixture closes F-01 mixed list plus adjacent plain-text tail false-positive", () => {
  const result = runFixture("fail-mixed-list-plain-tail.md");
  assert.equal(result.status, 1);
  assert.equal(result.output.status, "MECHANICAL_PRESENTATION_FAIL");
  assert.ok(failedCheckIds(result.output).includes("itemized_section_source_structure"));
  const section = result.output.rendered_section_evidence.find(
    (entry) => entry.heading === "三个重点"
  );
  assert.equal(section.sourceListItemCount, 2);
  assert.equal(section.nonBlankLineCount, 3);
  assert.equal(section.renderedListItemCount, 2);
  assert.equal(section.unstructuredInlineTails.length, 1);
  assert.equal(section.unstructuredInlineTails[0].text, "第三项");
});

test("PASS fixture does not misclassify blank-line-separated transition or ordinary prose", () => {
  const result = runFixture("pass-itemized-with-transition.md");
  assert.equal(result.status, 0, result.stderr || result.stdout);
  assert.equal(result.output.status, "MECHANICAL_PRESENTATION_PASS");
  const section = result.output.rendered_section_evidence.find(
    (entry) => entry.heading === "三个重点"
  );
  assert.equal(section.sourceListItemCount, 3);
  assert.equal(section.renderedListItemCount, 3);
  assert.deepEqual(section.unstructuredInlineTails, []);
});
