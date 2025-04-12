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
    console.log('Subtickets data:', subticketsData);

    if (subticketsData && subticketsData.length > 0) {
        // サブチケットテーブルを作成
        var table = $('<table class="listing subtickets">');
        var thead = $('<thead>');
        var headerRow = $('<tr>');
        headerRow.append($('<th>').text('ID'));
        headerRow.append($('<th>').text('Summary'));
        headerRow.append($('<th>').text('Status'));
        headerRow.append($('<th>').text('Owner'));
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
            row.append($('<td>').text(subticket.owner || ''));
            tbody.append(row);
        });
        table.append(tbody);

        // サブチケットセクションを作成
        var subticketsSection = $('<div class="subtickets-section">');
        subticketsSection.append($('<h2>').text('Subtickets'));
        subticketsSection.append(table);

        // 説明の後に追加
        descriptionElement.after(subticketsSection);
        console.log('Added subtickets section after description');
    } else {
        console.log('No subtickets found');
    }
});
