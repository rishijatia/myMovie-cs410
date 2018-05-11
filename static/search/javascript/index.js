(function() {
  var do_search, print_results, set_ranker_callbacks;

  $(function() {
    window.ranker = "OkapiBM25";
    set_ranker_callbacks();
    $(".input-group").keypress(function(k) {
      if (k.which === 13) {
        $("#search_button").click();
        return false;
      }
    });
    return $("#search_button").click(function() {
      return do_search();
    });
  });

  do_search = function() {
    var query;
    query = $("#query_text").val();
    if (query.length !== 0) {
      $("#search_results_list").empty();
      return $.ajax("search-api", {
        type: "POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
          query: query,
          ranker: window.ranker
        }),
        success: function(data, stat, xhr) {
          return print_results(data);
        },
        failure: function(axhr, stat, err) {
          return $("#search_results_list").append("<li>Something bad happened!</li>");
        }
      });
    }
  };

  set_ranker_callbacks = function() {
    $("#OkapiBM25").click(function() {
      window.ranker = "OkapiBM25";
      $("#search_concept").text("Okapi BM25");
      return do_search();
    });
    $("#PivotedLength").click(function() {
      window.ranker = "PivotedLength";
      $("#search_concept").text("Pivoted Length");
      return do_search();
    });
    $("#DirichletPrior").click(function() {
      window.ranker = "DirichletPrior";
      $("#search_concept").text("Dirichlet Prior");
      return do_search();
    });
    $("#JelinekMercer").click(function() {
      window.ranker = "JelinekMercer";
      $("#search_concept").text("Jelinek-Mercer");
      return do_search();
    });
    return $("#AbsoluteDiscount").click(function() {
      window.ranker = "AbsoluteDiscount";
      $("#search_concept").text("Absolute Discount");
      return do_search();
    });
  };

  print_results = function(result) {
    var displayed, doc, html, i, len, ref, results;
    if (result.results.length === 0) {
      $("#search_results_list").append('<p>No results found!</p>');
      return;
    }
    displayed = 0;
    ref = result.results;
    results = [];
    for (i = 0, len = ref.length; i < len; i++) {
      doc = ref[i];
      console.log(doc);
      if (displayed === 20) {
        break;
      }
      displayed += 1;
      html = '<a href="' + doc.path + '" class="list-group-item list-group-item-action flex-column align-items-start"> <div class="d-flex w-100 justify-content-between">'
      + '<h5 class="mb-1"><b>' + doc.name + '</b><small class="pull-right">' + doc.score.toFixed(4) + '</small></h5></div><p class="mb-1">' +
      'Release Date: ' + doc.year + '</p><small>' +
      'Gross Box Office Earning: $' + doc.gross + '</small></a>'
      console.log(html);
      results.push($("#search_results_list").append(html));
    }
    return results;
  };

}).call(this);
