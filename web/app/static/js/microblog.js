function refreshblog(formData) {
    $(".contentnew").remove();
    for (let i = 0 ; i < formData.length ; i++) {
        $("#tweet").prepend('<div class="row contentnew" id="' + formData[i].id + '">' +
            '<div class="col-md-11 content_cctv" id="content_cctv">' +
            '<div class="row tweet-info">' +
            '<div class="col-md-auto">' +
            '<img class="tw-user-medium rounded-circle" id="iconn" src="static/img/Nyan_cat.png">' +
            '<span class="tweet-username" id="tweet-username">' + formData[i].name + '</span>' +
            '<span class="tweet-usertag text-muted" id="tweet-usertag"> @' + formData[i].email + '</span>' +
            '<span class="tweet-age text-muted" id="tweet-age"> - ' + formData[i].date + '</span>' +
            '</div>' +
            '</div>' +
            '<div>' +
            '<p id="tweet-text">' +
            formData[i].message +
            '</p>' +
            '</div>' +
            '<div id="edit_remove">' +
            '<input type="button"' + '" value="✏️" onclick="prePopulateForm('+ formData[i].id +')">'+
            '<input type="button"' + '" value="🗑️" onclick="removeItem('+ formData[i].id +')">' +
            '</div>' +
            '</div>' +
            '</div>');
    }
}

$(document).ready(function () {
    (function () {
        $.getJSON("/lab11/microblogs", refreshblog);
    })();
});

$("#addNewBlogForm").submit(function (event) {
    // prevent default html form submission action
    event.preventDefault();

    var date = new Date();
    var offset = date.getTimezoneOffset();
    var offset1 = date.getTime();
    var timee = offset + offset1;
    document.getElementById("date").value = date.toLocaleString(timee, "en-US", {
        dateStyle: "full",
        timeStyle: "full"
    });

    // pack the inputs into a dictionary
    var formData = {};
    $(":input").each(function () {
        var key = $(this).attr('name');
        var val = $(this).val();
        if (key != 'submit') {
            formData[key] = val;
        }
    });

    // make a POST call to the back end w/ a callback to refresh the table
    $.post('/microblog', formData, function (blogData) {
        refreshblog(blogData)
        clearForm();
    });

    toggleView();
});


function clearForm() {
    $('#addNewBlogForm')[0].reset();
    $('#entryid').val('');
}

function prePopulateForm(id) {
    $('#addNewBlogForm')[0].reset();
    $.getJSON("/lab11/microblogs", function( data ) {
        
    });
    $('#name').val(data[id].name);
    $('#message').val(data[id].message);
    $('#email').val(data[id].email);
    $('#entryid').val(id);
    toggleView()
}

function removeItem(id) {
    if (!confirm("Delete " + '?')) {
        return false;
    }

    var url = "lab11/remove_content"
    var formData = { 'id': id };
    $.post(url, formData, function (blogData) {
        refreshblog(blogData);
    });

    $("#").detach();
}

function toggleView() {
    if ($('#blog_display').attr('hidden')) {
        $('#blog_display').removeAttr('hidden');
        $('#add-edit').attr('hidden', 'hidden');
    } else {
        $('#blog_display').attr('hidden', 'hidden');
        $('#add-edit').removeAttr('hidden');
    }
}

$("#add_blog").click(function () {
    clearForm();
    toggleView();
});

$("#clear_form").click(function () {
    clearForm();
});

$("#cancel_form").click(function () {
    clearForm();
    toggleView();
});