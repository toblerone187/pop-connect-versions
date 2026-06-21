#!/usr/bin/env python3
"""
build-franchise.py
==================
Generates PopConnect-franchise-attendance-template.html from
PopConnect-attendance-template.html by applying franchise-specific patches.

Run this at the end of every session after updating the master template:
    python3 build-franchise.py

The franchise file is never edited directly — always generated from the master.
"""

import re
import sys
import os

MASTER  = 'PopConnect-attendance-template.html'
OUTPUT  = 'PopConnect-franchise-attendance-template.html'

def build(src_path, out_path):
    with open(src_path, 'r', encoding='utf-8') as f:
        h = f.read()

    patches = []

    # ── 1. Page title ────────────────────────────────────────────────────────
    old = '<title>Pop Connect \u2014 Attendance Sheet Generator</title>'
    new = '<title>Pop Connect Franchise \u2014 Attendance Sheet Generator</title>'
    assert old in h, 'PATCH FAILED: title'
    h = h.replace(old, new); patches.append('title')

    # ── 2. Page heading ───────────────────────────────────────────────────────
    old = '    <h1>Pop Connect \u2014 Attendance Sheet Generator</h1>'
    new = '    <h1>Pop Connect Franchise \u2014 Attendance Sheet Generator</h1>'
    assert old in h, 'PATCH FAILED: heading'
    h = h.replace(old, new); patches.append('heading')

    # ── 3. Subheading ─────────────────────────────────────────────────────────
    old = '  <p style="font-size:11px;color:var(--grey-text);margin-top:2px;font-style:italic;">Powered by Pop Franchising Limited</p>'
    new = '  <p style="font-size:11px;color:var(--grey-text);margin-top:2px;font-style:italic;">Franchise version \u2014 powered by Pop Franchising Limited</p>'
    if old in h:
        h = h.replace(old, new); patches.append('subheading')

    # ── 4. Franchise fields in meeting details section ────────────────────────
    old = '''        <div class="form-group">
          <label>Host Name</label>
          <input type="text" id="hostName" value="" placeholder="Host name">
        </div>
      </div>
    </div>
  </div>

  <!-- Members -->'''
    new = '''        <div class="form-group">
          <label>Host Name</label>
          <input type="text" id="hostName" value="" placeholder="Host name">
        </div>
      </div>
      <div style="margin-top:14px;">
        <div style="font-size:11px;font-weight:700;color:var(--grey-text);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Franchise Details</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div class="form-group">
            <label>Franchisee Company Name</label>
            <input type="text" id="franchiseCompany" value="" placeholder="e.g. Smith Networking Ltd" oninput="updateFranchisePreview()">
          </div>
          <div class="form-group">
            <label>Territory</label>
            <input type="text" id="franchiseTerritory" value="" placeholder="e.g. Norfolk South" oninput="updateFranchisePreview()">
          </div>
        </div>
        <div style="font-size:11px;color:var(--grey-text);margin-top:8px;font-style:italic;" id="franchisePreviewLine">Enter company name and territory above.</div>
      </div>
    </div>
  </div>

  <!-- Members -->'''
    assert old in h, 'PATCH FAILED: franchise fields'
    h = h.replace(old, new); patches.append('franchise fields')

    # ── 5. updateFranchisePreview() function ──────────────────────────────────
    old = 'function saveMembers() {'
    new = '''function updateFranchisePreview() {
  const co = document.getElementById('franchiseCompany')?.value || '[Company]';
  const ter = document.getElementById('franchiseTerritory')?.value || '[Territory]';
  const el = document.getElementById('franchisePreviewLine');
  if (el) el.textContent = `Pop Connect ${ter} is a franchise independently owned and operated by ${co} with the written consent of Pop Franchising Limited`;
}

function saveMembers() {'''
    assert old in h, 'PATCH FAILED: updateFranchisePreview fn'
    h = h.replace(old, new); patches.append('updateFranchisePreview fn')

    # ── 6. Franchise notice in Word output ────────────────────────────────────
    old = "    bodyParts.push('<w:sectPr>"
    new = """    // Franchise notice at bottom of last page
    const franchiseCo = esc(document.getElementById('franchiseCompany')?.value || '');
    const franchiseTer = esc(document.getElementById('franchiseTerritory')?.value || '');
    if (franchiseCo && franchiseTer) {
      const franchiseNotice = `Pop Connect ${franchiseTer} is a franchise independently owned and operated by ${franchiseCo} with the written consent of Pop Franchising Limited`;
      bodyParts.push(`<w:p><w:pPr><w:spacing w:after="0" w:before="400"/><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:i/><w:sz w:val="18"/><w:szCs w:val="18"/><w:color w:val="666666"/></w:rPr><w:t xml:space="preserve">${franchiseNotice}</w:t></w:r></w:p>`);
    }
    bodyParts.push('<w:sectPr>"""
    assert old in h, 'PATCH FAILED: franchise notice in Word'
    h = h.replace(old, new); patches.append('franchise notice in Word')

    # ── 7. TEMPLATE_TYPE and UPDATE_FILE ─────────────────────────────────────
    old = """  const GROUP_SUFFIX = 'Pop Connect';
  const TEMPLATE_TYPE = 'standard';
  const UPDATE_FILE = 'PopConnect-attendance-template.html';"""
    new = """  const GROUP_SUFFIX = 'Pop Connect';
  const TEMPLATE_TYPE = 'franchise';
  const UPDATE_FILE = 'PopConnect-franchise-attendance-template.html';"""
    assert old in h, 'PATCH FAILED: TEMPLATE_TYPE'
    h = h.replace(old, new); patches.append('TEMPLATE_TYPE=franchise')

    # ── Write output ──────────────────────────────────────────────────────────
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(h)

    print(f'Built {out_path}')
    print(f'  Patches applied: {len(patches)}')
    for p in patches:
        print(f'    ✓ {p}')
    print(f'  Size: {len(h):,} bytes')

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else MASTER
    out = sys.argv[2] if len(sys.argv) > 2 else OUTPUT

    if not os.path.exists(src):
        print(f'ERROR: source file not found: {src}')
        sys.exit(1)

    try:
        build(src, out)
    except AssertionError as e:
        print(f'ERROR: {e}')
        print('The master template may have changed in a way that broke a patch.')
        print('Update build-franchise.py to match the new structure.')
        sys.exit(1)
