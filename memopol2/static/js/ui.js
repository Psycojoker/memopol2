jQuery.noConflict();

// replace mugshot by placeholder on errors
// --------------------------------------

function onMugshotError(source) {
    source.src = "/static/img/default-mugshot.png";
    source.className = "defaultMugshot";
    source.onerror = "";
    return true;
}

(function($) {

$.parseQuery = function(query) {
    // jQuery do not provide any helper to arse query strings, it's a shame…
    var hash = {};
    pairs = query.split('&');
    for (var i = 0; i < pairs.length; ++i)
    {
        var pair = pairs[i].split('=');
        if (pair.length != 2) {
            hash[pair[0]] = null;
        } else {
            hash[pair[0]] = decodeURIComponent(pair[1].replace(/\+/g, " "));
        }
    }
    return hash;
};

$('#content h1:first').addClass('document-title');

var FILTERS_SELECT_LABEL = "Select...";// FIXME: not suitable for I18n
// table
$("table.mep-list").tablesorter();
$("table.mp-list").tablesorter({ headers: { 2: { sorter: false }, }  });
$("table.mp-list, table.mep-list").tableFilter({
    selectOptionLabel: FILTERS_SELECT_LABEL, 
    enableCookies: false,
    filteredRows: function() {
        $("table.mp-list, table.mep-list").trigger('filteredRows');
    }
});

function FilterExtension(table) {
    this.table = $(table);
    var filtersBackup = this.filtersBackup = [];
    this.table.find('.filters .filter').each(function(index, filter) {
        filtersBackup[index] = $(filter).children().clone();
    });
    this.table.bind('filteredRows', $.proxy(this, 'refresh'));
    this.buildIndexes();
    this.refresh(false);

    var callback =  $.proxy(this, 'onQueryChanged');
    $(document).ready(callback)
    $(window).bind('hashchange', callback);
}

FilterExtension.prototype.BASE_HASH = '#!filters?';

FilterExtension.prototype.BASE_HASH_RE = /^#!filters\?/;

FilterExtension.prototype.buildIndexes = function() {
    var nameIndex = this.nameIndex = {};
    var filterIndex = this.filterIndex = {};
    var $table = this.table;
    $table.find('thead th').each(function(index, header) {
        var match = $(header).attr('class').match(/row-(\w+)/);
        if (match) {
            var name = match[1];
            nameIndex[index] = name;
            filterIndex[name] = index;
        }
    });
};

FilterExtension.prototype.onQueryChanged = function() {
    var hash = window.location.hash;
    if (!hash.match(this.BASE_HASH_RE)) return false;
    var filters = $.parseQuery(hash.replace(this.BASE_HASH_RE, ''));

    for (var name in filters) {
        if (filters.hasOwnProperty(name)) {
            var filter = this.table.find('#filter_' + this.filterIndex[name]);
            filter.val(filters[name]);
        }
    }
    this.table.tableFilterRefresh();
};

FilterExtension.prototype.refresh = function(updateHash) {
    var hash = {};
    this.table.find('.filters .filter').each($.proxy(function(index, filter) {
        var $filter = $(filter);
        if (!this.isSelected($filter)) {
            // reset select from previous state
            var filterValue = $filter.val();
            $filter.empty().append(this.filtersBackup[index].clone()).val(filterValue);

            this.displayCounts($filter, this.countEntries($filter));
        } else {
            var filterIndex = parseInt($filter.attr('id').replace(/[^\d]+/, ''), 10);
            hash[this.nameIndex[filterIndex]] = $filter.val();
        }
    }, this));
    
    if (updateHash) {
        window.location.hash = $.isEmptyObject(hash) ? '' : this.BASE_HASH + $.param(hash);
    }
};

FilterExtension.prototype.isSelected = function(filter) {
    var filterValue = filter.val();
    return $.trim(filterValue) && filterValue != FILTERS_SELECT_LABEL;
};

FilterExtension.prototype.countEntries = function(filter) {
    var counts = {};
    var index = filter.parent().prevAll().length;
    var cells = this.table.find('tbody tr[filtermatch!=false] td:nth-child(' + (index + 1) + ')');
    cells.each(function(index, cell) {
        var html = $(cell).html();
        counts[html] = (counts[html] || 0) + 1;
    });
    return this.stripKeys(counts);
};

FilterExtension.prototype.displayCounts = function(filter, counts) {
    filter.find('option[value]').each($.proxy(function(index, option) {
        $option = $(option);
        count = counts[$.trim($option.val())] || 0;
        
        $option.html($option.html() + ' (' + count + ')');
        if (!count && !this.isSelected(filter)){
            $option.remove();
        }
    }, this));
};

FilterExtension.prototype.stripKeys = function(counts) {
    var stripedCounts = {};
    for (html in counts) {
        stripedCounts[jQuery.trim(html.replace(/<\/?[^>]+>/gi, ''))] = counts[html];
    }
    return stripedCounts;
};

var filterExtension = new FilterExtension($("table.mep-list"));

$("table.mep-list tbody tr, table.mp-list tbody tr").hover(
    function() {$(this).addClass('odd');},
    function() {$(this).removeClass('odd');}
);

// collapsible elements
$(".collapsed~.body").hide();
$(".collapsible").click(function(){
    if ($(this).hasClass("collapsed"))
    {
        $(this).removeClass("collapsed").addClass("expanded");
        $(this).next(".body").show("fast");
    }
    else
    {
        $(this).removeClass("expanded").addClass("collapsed");
        $(this).next(".body").hide("fast");
    }
});


// contact details
$('body').delegate('a.more-contact', 'click', function() {
    // dynamic contact detail
    var $this = $(this);
    var $body = $this.parents('td').find('div.body');
    $body.data('previousState', $body.html()).load($this.attr('href'));
    return false;
});

$('body').delegate('a.less-contact', 'click', function() {
    var $body = $(this).parents('td').find('div.body');
    $body.html($body.data('previousState'));
    return false;
});

// the image #call-now click get his link from a.call-now from the contact details
$('a#call-now').attr('href', $('a.call-now').attr('href'));

// live search
var livesearch = $('#livesearch');
$.extend($, {
    livesearchtext: null,
    livesearchindex: -1,
    livesearchitems: null,
    livesearch: function(self, q) {
        if ($.livesearchtext == q) {
            q = self.val();
            q = q.replace(/\s+$/, '');
            if (!/\*$/.exec(q)) { q += '*'; }
            if ($('#search').length) {
                // serialize form and extract only types from qs
                q += '&' + $('#search').serialize().replace(/q=[^&]+/, '').substring(1);
            }
            $.get(livesearch.attr('alt')+'?limit=10&q='+q, function(data) {
                if (/li/.exec(data)) {
                    livesearch.html(data);
                    $.livesearchindex = -1;
                    $.livesearchitems = $('li', livesearch);
                    $.livesearchitems.hover(function() {
                        $.livesearchitems.removeClass('odd');
                        $(this).addClass('odd');
                    }, function() {
                        $(this).removeClass('odd');
                    });
                    livesearch.show();
                } else {
                    livesearch.hide();
                }
            });
        }
    }
});
$('input.search-text, #search #id_q').focus(function() {
    var self = $(this);
    var pos = self.offset();
    livesearch.css('left', pos.left);
    livesearch.css('top', pos.top+10+self.height());
});
$('input.search-text, #search #id_q').keydown(function(e) {
    var self = $(this);
    var code = (e.keyCode ? e.keyCode : e.which);
    if (code == 13) {
        // enter
        if ($.livesearchindex >= 0) {
            window.location.href = $('a', $.livesearchitems[$.livesearchindex]).attr('href');
            return false;
        }
    } else if (code == 40) {
        // up
        $.livesearchindex++;
        if ($.livesearchindex >= $.livesearchitems.length) {
            $.livesearchindex--;
        }
        $.livesearchitems.removeClass('odd');
        $($.livesearchitems[$.livesearchindex]).addClass('odd');
        return false;
    } else if (code == 38) {
        // down
        $.livesearchindex--;
        $.livesearchitems.removeClass('odd');
        if ($.livesearchindex >= 0) {
            $($.livesearchitems[$.livesearchindex]).addClass('odd');
        } else {
            $.livesearchindex = -1;
        }
        return false;
    } else {
        var q = self.val();
        if (q.length >= 2) {
            $.livesearchtext = q;
            setTimeout(function() {$.livesearch(self, q)}, 1000);
        }
    }
});
$('body').click(function() {livesearch.hide()});

}(jQuery));
