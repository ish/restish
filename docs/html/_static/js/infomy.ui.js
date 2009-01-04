if(typeof(infomy) == 'undefined') {
    infomy = {};
}

if(typeof(infomy.ui) == 'undefined') {
    infomy.ui = {};
}


infomy.ui.createDialog = function(d, e, ac) {
  d.dialog(options={'title': 'Add Organisation','height': 408});
  d.css('overflow','auto');
  d.submit( function () {
    D = $(d).serialize();
    $.ajax({
      type: "POST",
      url: U,
      data: D,
      success: function(html) { infomy.ui.openPostedDialog(d, html, e, ac); },
      error: function(error) { infomy.ui.openPostedDialog(d, error, e, ac); },
    });
    return false;
  });
};

infomy.ui.openPostedDialog = function(d, html, e, ac) {
  if ($(html).find('#formish .error').length == 0) {
    d.dialog('destroy');
    e.val($(html).find('#organisation-id').text());
    ac.val($(html).find('#organisation-name').text());
    return true;
  };
  d = $(html).find('#formish');
  $('#formish').html(d.html());
};

infomy.ui.openDialog = function(e, ac) {
  U = "/organisations/_new";
  $.get(U, function(content) {
    d = $(content).find('#formish');
    infomy.ui.createDialog(d, e, ac);
  });
};



infomy.ui.collection_to_autocomplete_list = function(collection) {
    return $.map(collection.items, function(item) {
            return {data: [item.name], value: item.id, result: item.name};
            });
}

infomy.ui.openDialogFactory = function(e,ac) {
  return function() {
    infomy.ui.openDialog(e, ac);
  }
}

infomy.ui.organisation_autocomplete = function(e) {
    var e = $(e);
    // Create an auto complete field for entering the organisation by name.
    var ac_input = $('<input />')
        .autocomplete({
                mustMatch: true,
                url: '/organisations',
                dataType: 'json',
                parse: infomy.ui.collection_to_autocomplete_list})
        .autocomplete('result', function(ev, data, value) {
                $(e).attr('value', value);
                });
    // Add an 'Add Organisation' button
    e.after($('<span>Add Organisation</span>').click(infomy.ui.openDialogFactory(e,ac_input)));
    // Fill in the org name.
    var org_id = e.attr('value');
    if(org_id != '') {
        $.getJSON('/organisations/'+org_id, function(org) {ac_input.attr('value', org.name)});
    }
    // Replace the org id with the auto complete field.
    e.hide().after(ac_input);
}



