const Newpost = document.querySelector('.Newpost');
const Popup = document.querySelector('#blog_display');
const Close = document.querySelector('.cclose');

function refreshblog(formData) {
    $(".item2").remove();
    var check = document.getElementsByClassName('emp')[0].id;
    for (let i = 0; i < formData.length; i++) {
        if (check == formData[i].email) {
            $("#blogPost").prepend(
                '<div class="item2" id="' + formData[i].id + '">'+
                '<div class="content">'+
                '<div class="card-img">'+
                '<img decoding="async" src="../../static/uploads/'+ formData[i].picname +'" alt="">'+
                '</div>'+
                '<div class="card-body">'+
                '<p>' + formData[i].message + '</p>'+
                '<div class="user">'+
                '<img decoding="async" src="../../static/uploads/'+ formData[i].avatar_url +'" alt="">'+
                '<div class="user-info">'+
                '<h5>' + formData[i].name + '</h5>'+
                '<small>' + formData[i].email + '</small>'+
                '<small id="time">' + formData[i].date + '</small>'+
                '</div>'+
                '</div>'+
                '</div>'+
                '<div id="edit_remove">' +
                '<input type="button" class="edit"' + '" value="✏️" onclick="prePopulateForm(' + formData[i].id + ')">' +
                '<input type="button" class="remove"' + '" value="🗑️" onclick="removeItem(' + formData[i].id + ')">' +
                '</div>'+
                '</div>'+
                '</div>'
                );
        } else {
            $("#blogPost").prepend(
                '<div class="item2" id="' + formData[i].id + '">'+
                '<div class="content">'+
                '<div class="card-img">'+
                '<img decoding="async" src="../../static/uploads/'+ formData[i].picname +'" alt="">'+
                '</div>'+
                '<div class="card-body">'+
                '<p>' + formData[i].message + '</p>'+
                '<div class="user">'+
                '<img decoding="async" src="'+ formData[i].avatar_url +'" alt="">'+
                '<div class="user-info">'+
                '<h5>' + formData[i].name + '</h5>'+
                '<small>' + formData[i].email + '</small>'+
                '<small id="time">' + formData[i].date + '</small>'+
                '</div>'+
                '</div>'+
                '</div>'+
                '</div>'+
                '</div>'
                );
        }
    }
}


$(document).ready(function () {
    (function () {
        $.getJSON("/review/blog", refreshblog);
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
    var formData = new FormData();
    $(".addpost").each(function () {
        var key = $(this).attr('name');
        var val = $(this).val();
        if (key != 'submit') {
            formData.append(key,val);
        }
    });
    formData.append("file", document.getElementById('file').files[0]);
    // make a POST call to the back end w/ a callback to refresh the table
    $.ajax({
        url:'/review',
        type:'post',
        data:formData,
        contentType: false,
        processData: false,
        success:function(response){
            refreshblog(response)
            clearForm_1();
            Newpost.classList.remove('active-popup');
        }
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
    var url = "/project/remove-review"
    var formData = { 'id': id };
    $.post(url, formData, function (blogData) {
        refreshblog(blogData);
    });

    $("#").detach();
}

$("#add_blog").click(function () {
    clearForm_1();
});

$("#clear_form").click(function () {
    clearForm();
});

$("#cancel_form").click(function () {
    clearForm_1();
    Newpost.classList.remove('active-popup');
});

$("#logout").click(function () {
    clearForm();
    window.location.href = "lab12/logout";
});

Popup.addEventListener('click', () => {
    Newpost.classList.add('active-popup');
});

Close.addEventListener('click', () => {
    Newpost.classList.remove('active-popup');
});