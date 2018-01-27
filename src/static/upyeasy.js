function dept_onchange(frmselect) {frmselect.submit();}

jQuery(function () {
	jQuery('form').bind('submit', function () {
		jQuery(this).find(':disabled').removeProp('disabled');
	});
});

$(document).on('submit', 'form', function() {
    $(this).find('input[type=checkbox]').each(function() {
        var checkbox = $(this);

        // add a hidden field with the same name before the checkbox with value = 0
        if ( !checkbox.prop('checked') ) {
            checkbox.clone()
                .prop('type', 'hidden')
                .val('off')
                .insertBefore(checkbox);
        }
    });
});