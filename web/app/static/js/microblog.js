function refreshblog(formData) {
    $(".contentnew").remove();
    // $("#tweet").prepend("")
    var check = document.getElementsByClassName('emp')[0].id;
    for (let i = 0; i < formData.length; i++) {
        if (check == formData[i].email) {
            $("#tweet").prepend('<div class="row contentnew" id="' + formData[i].id + '">' +
                '<div class="col-md-11 content_cctv" id="content_cctv">' +
                '<div class="row tweet-info">' +
                '<div class="col-md-auto">' +
                '<img class="tw-user-medium rounded-circle" id="iconn" src="'+ formData[i].avatar_url +'">' +
                '<span class="tweet-username textt" id="tweet-username">' + formData[i].name + '</span>' +
                '<span class="tweet-usertag text-muted textt" id="tweet-usertag"> ' + formData[i].email + '</span>' +
                '<span class="tweet-age text-muted textt" id="tweet-age"> - ' + formData[i].date + '</span>' +
                '</div>' +
                '</div>' +
                '<div>' +
                '<p id="tweet-text" class="textt">' +
                formData[i].message +
                '</p>' +
                '</div>' +
                '<div id="edit_remove">' +
                '<input type="button" class="edit"' + '" value="✏️" onclick="prePopulateForm(' + formData[i].id + ')">' +
                '<input type="button" class="remove"' + '" value="🗑️" onclick="removeItem(' + formData[i].id + ')">' +
                '</div>' +
                '</div>' +
                '</div>');
        } else {
            $("#tweet").prepend('<div class="row contentnew" id="' + formData[i].id + '">' +
                '<div class="col-md-11 content_cctv" id="content_cctv">' +
                '<div class="row tweet-info">' +
                '<div class="col-md-auto">' +
                '<img class="tw-user-medium rounded-circle" id="iconn" src="'+ formData[i].avatar_url +'">' +
                '<span class="tweet-username textt" id="tweet-username">' + formData[i].name + '</span>' +
                '<span class="tweet-usertag text-muted textt" id="tweet-usertag"> ' + formData[i].email + '</span>' +
                '<span class="tweet-age text-muted textt" id="tweet-age"> - ' + formData[i].date + '</span>' +
                '</div>' +
                '</div>' +
                '<div>' +
                '<p id="tweet-text" class="textt">' +
                formData[i].message +
                '</p>' +
                '</div>' +
                '<div id="edit_remove">' +
                '</div>' +
                '</div>' +
                '</div>');
        }
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
        clearForm_1();
    });

    toggleView();
});


function clearForm() {
    $('#addNewBlogForm')[0].reset();
    $('#entryid').val('');
}

function clearForm_1() {
    $('#message').val('');
    $('#entryid').val('');
    $('#date').val('');
}

function prePopulateForm(id) {
    $('#addNewBlogForm')[0].reset();
    $.getJSON("/lab11/microblogs", function (data) {
        console.log(data);
        var keyToFind = id;
        for (var i in data) {
            if (data[i].id == keyToFind) {
                $('#name').val(data[i].name);
                $('#message').val(data[i].message);
                $('#email').val(data[i].email);
                $('#entryid').val(id);
                break;
            }
        }
    });
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
    clearForm_1();
    toggleView();
});

$("#clear_form").click(function () {
    clearForm();
});

$("#cancel_form").click(function () {
    clearForm_1();
    toggleView();
});

$("#logout").click(function () {
    clearForm();
    window.location.href = "lab12/logout";
});