let addButton = document.querySelector("#add-form");
addButton.addEventListener("click", addForm);

function addForm(e) {
    let forms = document.querySelectorAll(
        ".trend-analysis-form-list > .trend-analysis-form"
    );
    let newFormIndex = forms.length;
    let numForms = forms.length + 1;
    let formTemplateNode = document.querySelector(
        ".trend-analysis-empty-form-container"
    );
    let container = document.querySelector(".trend-analysis-form-list");
    let totalFormsInput = document.querySelector(
        "#id_trend_analysis-TOTAL_FORMS"
    ); //management form inputs

    e.preventDefault();
    let formRegex = RegExp(`trend_analysis-__prefix__-`, "g");
    console.log(formRegex);
    let newFormHtml = formTemplateNode.innerHTML.replace(
        formRegex,
        `trend_analysis-${newFormIndex}-`
    );

    let newForm = document.createElement("tr");
    newForm.classList.add("trend-analysis-form");
    newForm.innerHTML = newFormHtml;
    container.appendChild(newForm);
    totalFormsInput.setAttribute("value", `${numForms}`);

    // a11y: focus on first input of newly added form
    newForm.querySelector("select,input").focus();
    updateInvisibleRowLabels();
}


let rowWord = "Entry";
if (window.location.href.includes("fr-ca")) {
    rowWord = "Entrée";
}
function updateInvisibleRowLabels() {
    document.querySelectorAll(".trend-analysis-form").forEach(function (row) {
        const yearInput = row.querySelector(
            'input[name$="-year"]'
        )
        const yearText = yearInput.value;
        const rowLabelSpan = row.querySelector('span[id$="-row-label"] .year-key');
        if (yearText.trim()) {
            rowLabelSpan.textContent = yearText;
        } else {
            rowIndex = Array.from(row.parentNode.children).indexOf(row) + 1;
            rowLabelSpan.textContent = `${rowWord} ${rowIndex}`;
        }
    });
}


updateInvisibleRowLabels();

document.addEventListener("change", function (e) {
    updateInvisibleRowLabels();
});
