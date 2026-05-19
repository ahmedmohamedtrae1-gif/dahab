document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('input, textarea, select').forEach(function (el) {
    if (!el.classList.contains('input')) el.classList.add('input');
  });

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.style.colorScheme = theme;
    try { localStorage.setItem('theme', theme); } catch (e) { }
    var label = document.querySelector('[data-theme-toggle] .theme-label');
    if (label) label.textContent = theme === 'dark' ? 'وضع فاتح' : 'وضع داكن';
  }

  (function initThemeToggle() {
    var toggle = document.querySelector('[data-theme-toggle]');
    if (!toggle) return;
    var current = document.documentElement.getAttribute('data-theme') || 'light';
    setTheme(current);
    toggle.addEventListener('click', function () {
      var next = (document.documentElement.getAttribute('data-theme') || 'light') === 'dark' ? 'light' : 'dark';
      setTheme(next);
    });
  })();

  function safeParseJSON(value) {
    try {
      return JSON.parse(value);
    } catch (e) {
      return null;
    }
  }

  function normalizeString(value) {
    return (value == null ? '' : String(value)).trim();
  }

  function createEl(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === 'class') el.className = attrs[k];
        else if (k === 'text') el.textContent = attrs[k];
        else el.setAttribute(k, attrs[k]);
      });
    }
    return el;
  }

  function initCompanions() {
    var hiddenInputs = document.querySelectorAll('input[data-companions-input="1"]');
    if (!hiddenInputs.length) return;

    function closeAllSelectMenus(except) {
      document.querySelectorAll('.select-menu.is-open').forEach(function (el) {
        if (except && el === except) return;
        el.classList.remove('is-open');
      });
    }

    document.addEventListener('click', function (e) {
      var menu = e.target && e.target.closest ? e.target.closest('.select-menu') : null;
      closeAllSelectMenus(menu);
    });

    hiddenInputs.forEach(function (hidden) {
      var fieldName = hidden.getAttribute('name');
      var addBtn = document.querySelector('.companions-add[data-companions-for="' + fieldName + '"]');
      var listEl = document.querySelector('.companions-list[data-companions-list="' + fieldName + '"]');
      if (!addBtn || !listEl) return;

      var initial = safeParseJSON(hidden.value);
      var items = Array.isArray(initial) ? initial : [];

      function sync() {
        hidden.value = JSON.stringify(items);
      }

      function wrapSelect(selectEl) {
        var menu = createEl('div', { class: 'select-menu' });
        var trigger = createEl('button', { type: 'button', class: 'select-trigger' });
        var label = createEl('span', { class: 'select-trigger-label' });
        var icon = createEl('span', { class: 'select-trigger-icon', 'aria-hidden': 'true' });
        trigger.appendChild(label);
        trigger.appendChild(icon);

        var list = createEl('div', { class: 'select-options', role: 'listbox' });
        Array.prototype.slice.call(selectEl.options).forEach(function (opt) {
          var item = createEl('button', { type: 'button', class: 'select-option', role: 'option', 'data-value': opt.value, text: opt.textContent });
          item.disabled = opt.disabled;
          item.addEventListener('click', function () {
            selectEl.value = opt.value;
            selectEl.dispatchEvent(new Event('change', { bubbles: true }));
            menu.classList.remove('is-open');
            sync();
          });
          list.appendChild(item);
        });

        function refresh() {
          var current = selectEl.value;
          var currentOpt = selectEl.options[selectEl.selectedIndex];
          label.textContent = currentOpt ? currentOpt.textContent : '';
          Array.prototype.slice.call(list.querySelectorAll('.select-option')).forEach(function (btn) {
            if (btn.getAttribute('data-value') === current) btn.classList.add('is-selected');
            else btn.classList.remove('is-selected');
          });
        }

        selectEl.classList.add('select-native-hidden');
        selectEl.addEventListener('change', function () {
          refresh();
        });

        trigger.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          var willOpen = !menu.classList.contains('is-open');
          closeAllSelectMenus(menu);
          if (willOpen) menu.classList.add('is-open');
          else menu.classList.remove('is-open');
        });

        trigger.addEventListener('keydown', function (e) {
          if (e.key === 'Escape') {
            menu.classList.remove('is-open');
            e.preventDefault();
          }
        });

        menu.appendChild(trigger);
        menu.appendChild(list);
        menu.appendChild(selectEl);
        refresh();
        return menu;
      }

      function buildCard(item, idx) {
        var card = createEl('div', { class: 'panel companions-card' });
        var head = createEl('div', { class: 'companions-card-head' });
        head.appendChild(createEl('strong', { text: 'مرافق #' + (idx + 1) }));
        var removeBtn = createEl('button', { type: 'button', class: 'secondary-btn companions-remove', text: 'حذف' });
        removeBtn.addEventListener('click', function () {
          items.splice(idx, 1);
          render();
          sync();
        });
        head.appendChild(removeBtn);
        card.appendChild(head);

        var grid = createEl('div', { class: 'companions-card-grid' });

        function addField(labelText, inputEl, wide) {
          var wrap = createEl('div', { class: 'field-wrap' + (wide ? ' wide' : '') });
          wrap.appendChild(createEl('label', { text: labelText }));
          wrap.appendChild(inputEl);
          grid.appendChild(wrap);
        }

        var nameInput = createEl('input', { type: 'text', class: 'input', placeholder: 'اسم المرافق' });
        nameInput.value = normalizeString(item.name);
        nameInput.addEventListener('input', function () {
          items[idx].name = nameInput.value;
          sync();
        });
        addField('الاسم', nameInput, false);

        var genderSelect = createEl('select', { class: 'input' });
        [
          { v: '', t: 'اختر النوع' },
          { v: 'ذكر', t: 'ذكر' },
          { v: 'أنثى', t: 'أنثى' }
        ].forEach(function (opt) {
          var o = createEl('option', { value: opt.v, text: opt.t });
          genderSelect.appendChild(o);
        });
        genderSelect.value = normalizeString(item.gender);
        genderSelect.addEventListener('change', function () {
          items[idx].gender = genderSelect.value;
          sync();
        });
        addField('النوع', wrapSelect(genderSelect), false);

        var phoneInput = createEl('input', { type: 'text', class: 'input', placeholder: 'رقم التليفون / واتساب', inputmode: 'tel' });
        phoneInput.value = normalizeString(item.phone);
        phoneInput.addEventListener('input', function () {
          items[idx].phone = phoneInput.value;
          sync();
        });
        addField('التليفون / واتساب', phoneInput, false);

        var ageInput = createEl('input', { type: 'number', class: 'input', placeholder: 'السن', min: '0' });
        ageInput.value = normalizeString(item.age);
        ageInput.addEventListener('input', function () {
          items[idx].age = ageInput.value;
          sync();
        });
        addField('السن', ageInput, false);

        var relationSelect = createEl('select', { class: 'input' });
        [
          { v: '', t: 'صلة القرابة' },
          { v: 'صديق', t: 'صديق' },
          { v: 'أب', t: 'أب' },
          { v: 'أم', t: 'أم' },
          { v: 'أخ', t: 'أخ' },
          { v: 'أخت', t: 'أخت' },
          { v: 'قريب', t: 'قريب' },
          { v: 'أخرى', t: 'أخرى' }
        ].forEach(function (opt) {
          var o = createEl('option', { value: opt.v, text: opt.t });
          relationSelect.appendChild(o);
        });
        relationSelect.value = normalizeString(item.relation);
        relationSelect.addEventListener('change', function () {
          items[idx].relation = relationSelect.value;
          if (relationSelect.value !== 'أخرى') items[idx].relation_other = '';
          render();
          sync();
        });
        addField('صلة القرابة', wrapSelect(relationSelect), false);

        if (normalizeString(item.relation) === 'أخرى') {
          var relationOtherInput = createEl('input', { type: 'text', class: 'input', placeholder: 'اكتب صلة القرابة' });
          relationOtherInput.value = normalizeString(item.relation_other);
          relationOtherInput.addEventListener('input', function () {
            items[idx].relation_other = relationOtherInput.value;
            sync();
          });
          addField('تحديد صلة القرابة', relationOtherInput, false);
        }

        var notesInput = createEl('textarea', { class: 'input', placeholder: 'ملاحظات', rows: '3' });
        notesInput.value = normalizeString(item.notes);
        notesInput.addEventListener('input', function () {
          items[idx].notes = notesInput.value;
          sync();
        });
        addField('ملاحظات', notesInput, true);

        card.appendChild(grid);
        return card;
      }

      function render() {
        listEl.innerHTML = '';
        items.forEach(function (item, idx) {
          if (!item || typeof item !== 'object') item = {};
          items[idx] = {
            name: normalizeString(item.name),
            gender: normalizeString(item.gender),
            phone: normalizeString(item.phone),
            age: normalizeString(item.age),
            notes: normalizeString(item.notes),
            relation: normalizeString(item.relation),
            relation_other: normalizeString(item.relation_other)
          };
          listEl.appendChild(buildCard(items[idx], idx));
        });
      }

      addBtn.addEventListener('click', function () {
        items.push({ name: '', gender: '', phone: '', age: '', notes: '', relation: '', relation_other: '' });
        render();
        sync();
      });

      if (!Array.isArray(initial)) {
        sync();
      }
      render();
    });
  }

  initCompanions();

  (function initSubmissionsSearch() {
    var input = document.querySelector('[data-submissions-search]');
    if (!input) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-submission-card]'));
    function filter() {
      var q = (input.value || '').trim().toLowerCase();
      cards.forEach(function (card) {
        var text = (card.textContent || '').toLowerCase();
        card.style.display = !q || text.indexOf(q) !== -1 ? '' : 'none';
      });
    }
    input.addEventListener('input', filter);
  })();

  (function initPrettyAnswers() {
    function isCompanionsArray(value) {
      return Array.isArray(value) && value.some(function (v) {
        return v && typeof v === 'object' && ('name' in v || 'gender' in v || 'phone' in v || 'relation' in v);
      });
    }

    function buildCompanionLine(item) {
      var line = createEl('div', { class: 'companion-line' });
      var title = createEl('div', { class: 'companion-title' });
      title.textContent = (item.name || '').trim() || 'مرافق';
      line.appendChild(title);

      var chips = createEl('div', { class: 'companion-chips' });
      function addChip(text) {
        if (!text) return;
        chips.appendChild(createEl('span', { class: 'companion-chip', text: text }));
      }

      addChip((item.gender || '').trim());
      addChip((item.age || '').toString().trim() ? ('سن: ' + (item.age || '').toString().trim()) : '');
      addChip((item.phone || '').trim() ? ('تليفون: ' + (item.phone || '').trim()) : '');
      var relation = (item.relation || '').trim();
      if (relation === 'أخرى') relation = ((item.relation_other || '').trim()) || 'أخرى';
      addChip(relation ? ('صلة: ' + relation) : '');
      if (chips.childNodes.length) line.appendChild(chips);

      if ((item.notes || '').trim()) {
        var note = createEl('div', { class: 'companion-note' });
        note.textContent = (item.notes || '').trim();
        line.appendChild(note);
      }
      return line;
    }

    document.querySelectorAll('[data-answer-value]').forEach(function (el) {
      var raw = (el.textContent || '').trim();
      if (!raw) return;
      var label = (el.getAttribute('data-answer-label') || '').trim();
      if (raw[0] !== '[' && raw[0] !== '{') return;
      var parsed = safeParseJSON(raw);
      if (!parsed) return;
      var shouldFormat = isCompanionsArray(parsed) || /مرافق|المرافق/i.test(label);
      if (!shouldFormat) return;

      var list = Array.isArray(parsed) ? parsed : (parsed && Array.isArray(parsed.items) ? parsed.items : []);
      if (!Array.isArray(list) || !list.length) return;

      var wrapper = createEl('div', { class: 'companions-inline' });
      list.forEach(function (item) {
        if (!item || typeof item !== 'object') return;
        if (!((item.name || '').trim())) return;
        wrapper.appendChild(buildCompanionLine(item));
      });
      if (!wrapper.childNodes.length) return;
      el.textContent = '';
      el.appendChild(wrapper);
    });
  })();
});
