(function($) {
  'use strict';
  
  // Expand entire sidebar on hover when it's minimized
  $(document).on('mouseenter', '.sidebar', function(ev) {
    var body = $('body');
    if (!('ontouchstart' in document.documentElement)) {
      if (body.hasClass("sidebar-icon-only")) {
        body.removeClass("sidebar-icon-only");
        body.addClass("sidebar-expanded-on-hover");
      }
    }
  });

  $(document).on('mouseleave', '.sidebar', function(ev) {
    var body = $('body');
    if (!('ontouchstart' in document.documentElement)) {
      if (body.hasClass("sidebar-expanded-on-hover")) {
        body.removeClass("sidebar-expanded-on-hover");
        body.addClass("sidebar-icon-only");
      }
    }
  });

  // Handle clicking the hamburger menu while hovered
  $('[data-toggle="minimize"]').on("click", function() {
    var body = $('body');
    if (body.hasClass("sidebar-expanded-on-hover")) {
      body.removeClass("sidebar-expanded-on-hover");
      // Prevent misc.js from double toggling by immediately returning
    }
  });

})(jQuery);