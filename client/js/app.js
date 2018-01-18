import './jquery-global';
import 'bootstrap';


class App {
  constructor($) {
    this.$ = $;
    this.toggleButtonState();
    this.navigateOnFilter();
  }

  toggleButtonState() {
    const $ = this.$;
    $('a[data-button-toggle-class]').on('click', function() {
      const $this = $(this);
      const klass = $(this).data('button-toggle-class');
      const shownClass = `btn-${klass}`;
      const hiddenClass = `btn-outline-${klass}`;
      // blur removes an ugly boostrap halo on :focus
      if ($this.hasClass(hiddenClass)) {
        $this.removeClass(hiddenClass).addClass(shownClass).blur();
      } else {
        $this.removeClass(shownClass).addClass(hiddenClass).blur();
      }
    });
  }

  navigateOnFilter() {
    const $ = this.$;
    $('#minion-filter').on('input', function() {
      const val = this.value;
      const datalist = document.getElementById(this.getAttribute('list'));
      const inDatalist = $(datalist).find('option').filter(function() {
        return this.value.toLowerCase() === val.toLowerCase();
      }).length;
      if (inDatalist) {
        $(this).parents('form').submit();
      }
    });
  }
}

new App(window.jQuery);

