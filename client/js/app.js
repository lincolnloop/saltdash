import './jquery-global';
import 'bootstrap';


class App {
  constructor($) {
    this.$ = $;
    this.$('a[data-toggle="collapse-optimized"]').on('click', this.toggleResultState.bind(this));
    this.$('#minion-filter').on('input', this.navigateOnFilter.bind(this));
  }
  
  toggleResultState(evt) {
    const $this = this.$(evt.currentTarget);
    const klass = $this.data('button-toggle-class');
    const shownClass = `btn-${klass}`;
    const hiddenClass = `btn-outline-${klass}`;
    // blur removes an ugly boostrap halo on :focus
    if ($this.hasClass(hiddenClass)) {
      $this.removeClass(hiddenClass).addClass(shownClass);
      this.$($this.data('target')).addClass(`state-${$this.data('target-status')}`);
    } else {
      $this.removeClass(shownClass).addClass(hiddenClass);
      this.$($this.data('target')).removeClass(`state-${$this.data('target-status')}`);
    }
    evt.preventDefault();
  }

  navigateOnFilter(evt) {
    const el = evt.currentTarget;
    const val = el.value;
    const datalist = document.getElementById(el.getAttribute('list'));
    const inDatalist = this.$(datalist).find('option').filter(function() {
      return this.value.toLowerCase() === val.toLowerCase();
    }).length;
    if (inDatalist) {
      this.$(el).parents('form').submit();
    }
    evt.preventDefault();
  }
}

new App(window.jQuery);

