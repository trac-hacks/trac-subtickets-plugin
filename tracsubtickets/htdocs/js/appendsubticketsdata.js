(function() {
    var $, args;
    
    $ = jQuery;

    // subtickets_script_args must have been defined via add_script_data()
    args = $.parseJSON(subtickets_script_args);

    createButton = function() {
        var form = $(`<form method="get" action="${args.href_req_newticket}"></form>`);
        var div = $(`<div class="inlinebuttons"></div>`);
        var submitButton = $(`<input type="submit" value="${args.localized_button_label}" title="${args.localized_button_title}"></input>`);
        var parentsArg = $(`<input type="hidden" name="parents" value="${args.parent_id}"></input>`);

        div.append(submitButton);
        div.append(parentsArg);
        $.each($.parseJSON(args.inherited_args), function(key, value) {
            var inheritedArg = $(`<input type="hidden" name="${key}" value="${value}"></input>`);
            div.append(inheritedArg);
        });

        form.append(div);

        return form;
    }

    createLink = function() {
        return $(`<span class="addsubticket">(<a href="${args.href_req_newticket_with_parent}">${args.localized_link_label}</a>)</span>`);
    }

    $(document).ready(function() {
        var div = $('<div class="description"></div>');
        var table = $('<table class="subtickets"></table>');
        
        $.each($.parseJSON(args.subtickets_table), function(key, value) {
            var row = $('<tr></tr>');
            row.append(value.summary);
            row.append(value.status);
            row.append(value.owner);
            table.append(row);
        });

        if (args.add_style == 'link') {
            var link = createLink();
            var separator = $(`<h3>${args.localized_separator_label}</h3>`);
            separator.append(link);
            div.append(separator);
        }
        else {
            var button = createButton();
            var separator = $(`<h3>${args.localized_separator_label}</h3>`);
            div.append(button);
            div.append(separator);
        }
        div.append(table);

        $('div#ticket').append(div);
    });

    // // content must have been defined via add_script_data()
    // $(document).ready(function() {
    //     $('div#ticket').append(content);
    // });

}).call(this);
