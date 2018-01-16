import './jquery-global';
import 'bootstrap';


class toggleState {
  constructor($) {
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
    })
  }
}

new toggleState(window.jQuery)

