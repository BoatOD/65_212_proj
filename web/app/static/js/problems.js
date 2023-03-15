$("#addForm").submit(function (event) {
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
    $.post('/problems/blog', formData, function (blogData) {
        refreshblog(blogData)
        clearForm_1();
    });

});

function clearForm_1() {
    $('#message').val('');
}