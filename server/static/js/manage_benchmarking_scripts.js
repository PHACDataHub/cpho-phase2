let addButton = document.querySelector("#add-form");
if (addButton) {
    addButton.addEventListener("click", addForm);
}

function addForm(e) {
    let forms = document.querySelectorAll(
        ".benchmarking-form-list > .benchmarking-form"
    );
    let newFormIndex = forms.length;
    let numForms = forms.length + 1;
    let formTemplateNode = document.querySelector(
        ".benchmarking-empty-form-container"
    );
    let container = document.querySelector(".benchmarking-form-list");
    let totalFormsInput = document.querySelector("#id_benchmarking-TOTAL_FORMS"); //management form inputs

    e.preventDefault();
    let formRegex = RegExp(`benchmarking-__prefix__-`, "g");
    console.log(formRegex);
    let newFormHtml = formTemplateNode.innerHTML.replace(
        formRegex,
        `benchmarking-${newFormIndex}-`
    );

    let newForm = document.createElement("tr");
    newForm.classList.add("benchmarking-form");
    newForm.innerHTML = newFormHtml;
    container.appendChild(newForm);
    totalFormsInput.setAttribute("value", `${numForms}`);

    // focus on first input of newly added form
    newForm.querySelector("select,input").focus();
}

// function updateInvisibleRowLabels() {

// }

// document.addEventListener("change", function (e) {
//     updateInvisibleRowLabels();
// });
