function isWhitespace(str) {
  return (str.length === 0 || !/\S/.test(str))
}

function checkInput() {
  let errors = false;
  let message = "The following issues have been found:\n";
  let type = $('#expType').val();

  let name = $("input[name=name]").val();
  if (isWhitespace(name)) {
    errors = true;
    message += " - Name must not be empty\n";
  }

  let testcases = $("input[name=" + type + "_testCases]:checked").length;
  let automated = (type !== 'Custom') || $('#automateCheckbox')[0].checked;
  if (automated && type !== "MONROE" && testcases === 0) {
    errors = true;
    message += " - Select at least one TestCase\n";
  }

  let application = $('#expApplication').val();
  if (type === "MONROE" && isWhitespace(application)) {
    errors = true;
    message += " - Application must not be empty\n";
  }

  let parameters = "";
  if (type === "Custom") { parameters = $("#customParameters").val(); }
  if (type === "MONROE") { parameters = $("#monroeParameters").val(); }

  if (!isWhitespace(parameters)) {
    try {
      JSON.parse(parameters);
    } catch(err) {
      errors = true;
      message += " - Could not parse Parameters as valid JSON:\n" + err;
    }
  }

  if (errors) { alert(message); }
  return !errors;
}

function changeNsRows(nss, nsIds) {
  curVal = $.trim($("#nsCount").val()).match(/^\d*$/);
  curFloors = $('.ns').length;
  if (curVal > curFloors) {
    addNs(curFloors, curVal, nss, nsIds);
  } else if (curVal < curFloors) {
    removeNs(curVal);
  }
}

function addNs(actual, target, nss, nsIds) {
  for (i = actual + 1; i <= target; i++) {
    newItemHTML = '<tr><td class="table-cell-divisor-right text-center">' + i + '</td><td class="table-cell-divisor-right"><select class="ns InputBox form-control" name="NS' + i + '">'
    for (j = 0; j < nss.length; j++) {
      newItemHTML = newItemHTML + '<option value="' + nsIds[j] + '">' + nss[j] + '</option>';
    }
    newItemHTML = newItemHTML + '</select></td></tr>';
    $("table#ns tr").last().after(newItemHTML);
  }
}

function removeNs(target) {
  if (target >= 0) {
    $('.ns').slice(target).parent().parent().remove();
  }
}

function disableSliceList() {
  let checkBox = document.getElementById('sliceNone');
  let sliceList = document.getElementById('sliceList');

  if (checkBox.checked === true) {
    sliceList.removeAttribute("disabled");
  } else {
    sliceList.setAttribute("disabled", true);
  }
}

function disableAutomatedSettings() {
  let checkbox = document.getElementById('automateCheckbox');
  let settings = document.getElementById('CustomAutomatedSettings');
  let reservation = document.getElementById('reservationCustom');
  settings.hidden = !checkbox.checked;
  reservation.disabled = checkbox.checked;
}

function changeSettingsDiv() {
  let type = $('#expType').val();
  $(".settingsDiv").hide();
  $("#"+type+"Settings").show();
}

function displayParameters() {
  let parameterRows = document.getElementsByClassName('parameter_row');
  for (let i = 0; i < parameterRows.length; i++) { parameterRows[i].style.display = 'none'; }

  let badges = document.getElementsByClassName('test_case_badge');
  for (let i = 0; i < badges.length; i++) { badges[i].style.display = 'none'; }

  let hasParameters = false;
  let checkboxes = document.getElementsByName('Custom_testCases');
  for (let i = 0; i < checkboxes.length; i++) {
    let checkbox = checkboxes[i];
    if (checkbox.checked) {
      let parameterNames = checkbox.dataset.testCaseParameters.trim().split(',');
      let testCaseName = checkbox.dataset.testCaseName.trim();

      for (let j = 0; j < parameterNames.length; j++) {
        let name = parameterNames[j];
        if (name.length > 0) {
          let parameterRow = document.getElementById(name + "_row");
          parameterRow.style.display = 'block';
          hasParameters = true;
        }
      }

      let testCaseBadges = document.getElementsByClassName(testCaseName + "_badge")
      for (let i = 0; i < testCaseBadges.length; i++) { testCaseBadges[i].style.display = 'inline'; }
    }

    document.getElementById('no_params_row').style.display = hasParameters ? 'none': 'block';
    document.getElementById('params_hint_row').style.display = hasParameters ? 'block': 'none';
  }
}