function count_previous_fields(o) {
  var f = o.prevAll('.field').length;
  var g = o.prevAll('.group').length;
  if (f > g) {
    return f;
  } else {
    return g;
  };
};   
   
function create_addlinks(o) {
  o.find('.adder').each(function() {
    $(this).before('<a class="adderlink">Add</a>');
  });
};

function get_sequence_numbers(segments, l) {
  var result = Array();
  for each (segment in segments) {
    if (isNaN(parseInt(segment)) == false) {
      result.push(segment);
    }
  }
  result.push(l);
  return result
}

function replace_stars(original, nums, divider) {
  var result = Array();
  var segments = original.split(divider);
  var n = 0;

  for each (segment in segments) {
    if ((segment == '*' || isNaN(parseInt(segment)) == false) && n < nums.length)   {
      // If the segment is a * or a number then we check replace it with the right number (the target number is probably right anyway)
      result.push(nums[n]);
      n=n+1;
    } else {
      // If not then we just push the segment
      result.push(segment);
    }
  }
  return result.join(divider);
}

function construct(start_segments, n, remainder, divider, strip) {
  var remainder_bits = remainder.split(divider);
  var remainder = remainder_bits.slice(1,remainder_bits.length-strip).join(divider);
  var result = Array();
  for each (segment in start_segments) {
    if (segment != '') {
      result.push(segment);
    }
  }
  result.push(n);
  if (remainder != '') {
      var out = result.join(divider)+divider+remainder;
  } else {
      var out = result.join(divider);
  }
  return out
};

function convert_id_to_name(s) {
  var segments=s.split('-');
  var out = segments.slice(1,segments.length).join('.');
  return out
}

function renumber_sequences(o) {
  var n = 0;
  var previous_seqid_prefix = '';
  o.find('.sequence > div').each( function () {
    var seqid = $(this).parent().attr('id');
    var seqid_prefix = seqid.substr(0,seqid.length-5);
    if (seqid_prefix != previous_seqid_prefix) {
      n = 0;
    } else {
      n=n+1;
    }    
    // replace id occurences
    var thisid = $(this).attr('id');
    var newid = seqid_prefix + n + '-field';
    $(this).attr('id',newid);
    // Replace 'for' occurences
    $(this).find("[for^='"+seqid_prefix+"']").each( function () {
      var name = $(this).attr('for');
      $(this).text(n);
      var name_remainder = name.substring(seqid_prefix.length, name.length);
      $(this).attr('for', construct(seqid_prefix.split('-'),n,name_remainder,'-', 1));
    });
    // Replace 'id' occurences
    $(this).find("[id^='"+seqid_prefix+"']").each( function () {
      var name = $(this).attr('id');
      var name_remainder = name.substring(seqid_prefix.length, name.length);
      $(this).attr('id', construct(seqid_prefix.split('-'),n,name_remainder,'-', 1));
    });
    // replace 'name' occurences
    $(this).find("[name^='"+convert_id_to_name(seqid_prefix)+"']").each( function () {
      var name = $(this).attr('name');
      var name_remainder = name.substring(convert_id_to_name(seqid_prefix).length, name.length);
      $(this).attr('name', construct(convert_id_to_name(seqid_prefix).split('.'),n,name_remainder,'.', 1));
    });
    previous_seqid_prefix = seqid_prefix;
  });
  o.find('.sequence > fieldset').each( function () {
    var seqid = $(this).parent().attr('id');
    var seqid_prefix = seqid.substr(0,seqid.length-5);
    if (seqid_prefix != previous_seqid_prefix) {
      n = 0;
    } else {
      n=n+1;
    }    
    // replace id occurences
    var thisid = $(this).attr('id');
    $(this).find('> legend').text(n);
    var newid = seqid_prefix + n + '-field';
    $(this).attr('id',newid);
    // Replace 'for' occurences
    $(this).find("[for^='"+seqid_prefix+"']").each( function () {
      var name = $(this).attr('for');
      var name_remainder = name.substring(seqid_prefix.length, name.length);
      $(this).attr('for', construct(seqid_prefix.split('-'),n,name_remainder,'-', 0));
    });
    // Replace 'id' occurences
    $(this).find("[id^='"+seqid_prefix+"']").each( function () {
      var name = $(this).attr('id');
      var name_remainder = name.substring(seqid_prefix.length, name.length);
      $(this).attr('id', construct(seqid_prefix.split('-'),n,name_remainder,'-', 0));
    });
    // replace 'name' occurences
    $(this).find("[name^='"+convert_id_to_name(seqid_prefix)+"']").each( function () {
      var name = $(this).attr('name');
      var name_remainder = name.substring(convert_id_to_name(seqid_prefix).length, name.length);
      $(this).attr('name', construct(convert_id_to_name(seqid_prefix).split('.'),n,name_remainder,'.',0));
    });
    previous_seqid_prefix = seqid_prefix;
  });

}

function add_mousedown_to_addlinks(o) {
  o.find('.adderlink').mousedown( function() {
    // Get the base64 encoded template
    var code = $(this).next('.adder').val();
    // Find out how many fields we already have
    var l = count_previous_fields($(this).next('.adder'));
    // Get some variable to help with replacing (originalname, originalid, name, id)
    var originalname = $(this).next('.adder').attr('name');
    var segments = originalname.split('.');
    // Get the numbers used in the originalname
    var seqnums = get_sequence_numbers(segments, l);
    var originalid = $(o).attr('id')+'-'+segments.join('-');
    segments[ segments.length -1 ] = l;
    var name = segments.join('.');
    var id = $(o).attr('id')+'-'+segments.join('-');
    // Decode the base64
    var html = $.base64Decode(code);
    // Add the links and mousedowns to this generated code
    var h = $(html);
    create_addlinks(h);
    add_mousedown_to_addlinks(h);

    h.find("[name]").each( function () {
      var newname = replace_stars($(this).attr('name'), seqnums, '.');
      $(this).attr('name', newname );
    });
    
    var newid = replace_stars(h.attr('id'),seqnums,'-')

    h.attr('id',newid);
    h.find("[id]").each( function () {
      var newid = replace_stars($(this).attr('id'),seqnums, '-');
      $(this).attr('id', newid );
    });
    h.find("[for]").each( function () {
      var newid = replace_stars($(this).attr('for'),seqnums, '-');
      $(this).attr('for', newid );
      if ($(this).text() == '*') {
        $(this).text(l);
      }
    });
    h.find("label[for='"+id+"']").text(l);
    h.find("legend:contains('*')").text(l);

    $(this).before(h);
    add_sortables($('form'));
    add_remove_buttons($(this).parent().parent());
  });
};

function add_remove_buttons(o) {
  o.find('.sequence.sequencecontrols > div > label').each( function() {
    if ($(this).next().text() != 'x') {
      var x = $('<span class="remove">x</span>');
      $(this).after(x);
      x.mousedown(function () {
        $(this).parent().remove();
        renumber_sequences($('form'));
        add_sortables($('form'));
      });
    };
  });
  o.find('.sequence.sequencecontrols > fieldset > legend').each( function() {
    if ($(this).next().text() != 'x') {
      var x = $('<span class="remove">x</span>');
      $(this).after(x);
      x.mousedown(function () {
        $(this).parent().remove();
        renumber_sequences($('form'));
        add_sortables($('form'));

      });
    };
  });
}

function order_changed(e,ui) {
  renumber_sequences($('form'));
}

function add_sortables(o) {
  //o.find('.sequence > div > label').after('<span class="handle">handle</span>');
  //o.find('.sequence > fieldset > legend').after('<span class="handle">handle</span>');
  o.find('.sequence').sortable({'items':'> div','stop':order_changed});
  
}

function formish() {
    create_addlinks($('form'));
    add_mousedown_to_addlinks($('form'));
    add_remove_buttons($('form'));
    add_sortables($('form'));
}