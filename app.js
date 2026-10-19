// 請求Hub デモ — 共通インタラクション（静的プロトタイプ用）
document.addEventListener('DOMContentLoaded', function () {
  var slice = function (n) { return Array.prototype.slice.call(n); };

  // --- 請求書一覧: 全選択 / 行ハイライト / 一括バー ---
  var selAll = document.querySelector('[data-selectall]');
  var rowChecks = slice(document.querySelectorAll('[data-rowcheck]'));
  var bulkbar = document.querySelector('[data-bulkbar]');
  var bulkcount = document.querySelector('[data-bulkcount]');

  function refreshBulk() {
    var n = rowChecks.filter(function (c) { return c.checked; }).length;
    rowChecks.forEach(function (c) {
      var tr = c.closest('tr');
      if (tr) tr.classList.toggle('sel', c.checked);
    });
    if (bulkbar) bulkbar.style.display = n > 0 ? 'flex' : 'none';
    if (bulkcount) bulkcount.textContent = n;
    if (selAll) {
      selAll.checked = n > 0 && n === rowChecks.length;
      selAll.indeterminate = n > 0 && n < rowChecks.length;
    }
  }
  if (selAll) selAll.addEventListener('change', function () {
    rowChecks.forEach(function (c) {
      var tr = c.closest('tr');
      // 絞り込みで非表示の行は対象にしない
      if (!tr || tr.style.display !== 'none') c.checked = selAll.checked;
    });
    refreshBulk();
  });
  rowChecks.forEach(function (c) { c.addEventListener('change', refreshBulk); });
  if (rowChecks.length) refreshBulk();

  // --- タブ絞り込み（状態で表示切替） ---
  var tabs = slice(document.querySelectorAll('[data-tab]'));
  var statusRows = slice(document.querySelectorAll('[data-status]'));
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('on'); });
      t.classList.add('on');
      var f = t.getAttribute('data-tab');
      statusRows.forEach(function (r) {
        r.style.display = (f === 'all' || r.getAttribute('data-status') === f) ? '' : 'none';
      });
      // 絞り込み後に選択状態を再計算
      if (rowChecks.length) {
        rowChecks.forEach(function (c) {
          var tr = c.closest('tr');
          if (tr && tr.style.display === 'none') c.checked = false;
        });
        refreshBulk();
      }
    });
  });

  // --- セグメント切替（請求書/見積書/納品書 など） ---
  slice(document.querySelectorAll('[data-seg]')).forEach(function (group) {
    var btns = slice(group.querySelectorAll('button'));
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
      });
    });
  });

  // --- 入金管理: 入金記録ボタンで行を選択 ---
  var recBtns = slice(document.querySelectorAll('[data-rec]'));
  var recHeader = document.querySelector('[data-recheader]');
  recBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      recBtns.forEach(function (x) {
        x.classList.remove('on');
        var r = x.closest('tr');
        if (r) r.classList.remove('on');
      });
      b.classList.add('on');
      var row = b.closest('tr');
      if (row) row.classList.add('on');
      if (recHeader) recHeader.textContent = '入金を記録 — ' + b.getAttribute('data-rec');
    });
  });

  // --- 請求書作成: 明細行の追加・削除 ---
  var itemsBox = document.querySelector('[data-items]');
  var addBtn = document.querySelector('[data-addrow]');
  if (itemsBox && addBtn) {
    addBtn.addEventListener('click', function () {
      var rw = document.createElement('div');
      rw.className = 'rw';
      rw.innerHTML =
        '<input value="" placeholder="品目を入力">' +
        '<input class="n" value="1">' +
        '<input value="式">' +
        '<input class="n" value="0">' +
        '<select><option>10%</option><option>8%</option></select>' +
        '<button class="del" aria-label="行を削除" data-del>×</button>';
      itemsBox.appendChild(rw);
    });
    itemsBox.addEventListener('click', function (e) {
      var d = e.target.closest('[data-del]');
      if (d) { var rw = d.closest('.rw'); if (rw) rw.remove(); }
    });
  }
});
