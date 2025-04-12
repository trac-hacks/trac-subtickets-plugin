$(document).ready(function() {
    console.log('Subtickets.js loaded');

    // Check if we are on a ticket page
    var descriptionElement = $('.description');
    if (!descriptionElement.length) {
        console.log('Description element not found');
        return;
    }

    // Get ticket ID from URL
    var match = window.location.pathname.match(/\/ticket\/(\d+)/);
    if (!match) {
        console.log('No ticket ID found in URL');
        return;
    }

    var ticketId = match[1];
    console.log('Processing ticket:', ticketId);

    // Get subticket data from Trac's script data
    var subticketsData = window.tracSubticketsData;
    var columnNames = window.columnNames;
    console.log('Subtickets data:', subticketsData);
    console.log('Column names:', columnNames);

    // Create subtickets section
    var subticketsSection = $('<div class="subtickets-section">');

    // Create title section (including new subticket button)
    var titleContainer = $('<div class="subtickets-header">');
    var title = $('<h2>').text('Subtickets');
    titleContainer.append(title);

    // Add new subticket button
    var newTicketUrl = window.location.pathname.replace(/\/ticket\/\d+$/, '/newticket') + '?parents=' + ticketId;
    var buttonContainer = $('<div>').addClass('buttons');
    var button = $('<a>')
        .addClass('newticket')
        .attr('href', newTicketUrl)
        .text('New subticket');
    buttonContainer.append(button);
    titleContainer.append(buttonContainer);

    subticketsSection.append(titleContainer);

    if (subticketsData && subticketsData.length > 0) {
        // Create subtickets table
        var table = $('<table class="listing subtickets">');
        var thead = $('<thead>');
        var headerRow = $('<tr>');
        headerRow.append($('<th>').text(columnNames.id));
        headerRow.append($('<th>').text(columnNames.summary));
        headerRow.append($('<th>').text(columnNames.status));
        headerRow.append($('<th>').text(columnNames.type));
        headerRow.append($('<th>').text(columnNames.priority));
        headerRow.append($('<th>').text(columnNames.owner));
        thead.append(headerRow);
        table.append(thead);

        var tbody = $('<tbody>');
        subticketsData.forEach(function(subticket) {
            var row = $('<tr>');

            // Create ID cell (with indentation)
            var idCell = $('<td>');
            // Add indentation based on level
            if (subticket.level > 0) {
                var indent = $('<span>').addClass('indent');
                for (var i = 0; i < subticket.level; i++) {
                    indent.append($('<span>').addClass('indent-level'));
                }
                idCell.append(indent);
            }
            // Add ticket ID link
            var ticketUrl = window.location.pathname.replace(/\/\d+$/, '') + '/' + subticket.id;
            idCell.append($('<a>').attr('href', ticketUrl).text('#' + subticket.id));
            row.append(idCell);

            // Add other cells
            row.append($('<td>').text(subticket.summary));
            row.append($('<td>').text(subticket.status));
            row.append($('<td>').text(subticket.type || ''));
            row.append($('<td>').text(subticket.priority || ''));
            row.append($('<td>').text(subticket.owner || ''));
            tbody.append(row);
        });
        table.append(tbody);
        subticketsSection.append(table);
    }

    // Add after description
    descriptionElement.after(subticketsSection);
    console.log('Added subtickets section after description');
});
