$(function () {
    var sizeIndex = 0;
    var colorIndex = 0;
    $eles = $("table.model-list th").each(function (i) {
        {
            if ($.trim($('a', this).text()) == 'Size') {
                sizeIndex = i;
            }
            if ($.trim($('a', this).text()) == 'Color') {
                colorIndex = i;
            }
        }
    });


    $("table.model-list tbody tr").each(function () {
        $("td", this).each(function (i) {
            if (i == sizeIndex) {
                $(this).css('font-size', parseInt($(this).text()) * 1.5 + 13 + 'px');
            }
            if (i == colorIndex) {
                $(this).css('color', $(this).text()).css({'text-shadow':'1px 1px 1px #000000','font-weight':'bolder','font-size':'20px'  })
            }
        });
    });
});