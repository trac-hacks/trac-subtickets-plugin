$(document).ready(function() {
    console.log('Subtickets.js loaded');

    // チケットページかどうかを確認
    var descriptionElement = $('.description');
    if (!descriptionElement.length) {
        console.log('Description element not found');
        return;
    }

    // チケットIDを取得
    var match = window.location.pathname.match(/\/ticket\/(\d+)/);
    if (!match) {
        console.log('No ticket ID found in URL');
        return;
    }

    var ticketId = match[1];
    console.log('Processing ticket:', ticketId);

    // Tracが提供するスクリプトデータからサブチケット情報を取得
    var subticketsData = window.tracSubticketsData;
    var columnNames = window.columnNames;
    console.log('Subtickets data:', subticketsData);
    console.log('Column names:', columnNames);

    // サブチケットセクションを作成
    var subticketsSection = $('<div class="subtickets-section">');

    // タイトル部分を作成（子チケット作成ボタンを含む）
    var titleContainer = $('<div class="subtickets-header">');
    var title = $('<h2>').text('Subtickets');
    titleContainer.append(title);

    // 子チケット作成ボタンを追加
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
        // サブチケットテーブルを作成
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

            // IDセルを作成（インデントを含む）
            var idCell = $('<td>');
            // レベルに応じたインデントを追加
            if (subticket.level > 0) {
                var indent = $('<span>').addClass('indent');
                for (var i = 0; i < subticket.level; i++) {
                    indent.append($('<span>').addClass('indent-level'));
                }
                idCell.append(indent);
            }
            // チケットIDのリンクを追加
            var ticketUrl = window.location.pathname.replace(/\/\d+$/, '') + '/' + subticket.id;
            idCell.append($('<a>').attr('href', ticketUrl).text('#' + subticket.id));
            row.append(idCell);

            // その他のセルを追加
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

    // 説明の後に追加
    descriptionElement.after(subticketsSection);
    console.log('Added subtickets section after description');
});
