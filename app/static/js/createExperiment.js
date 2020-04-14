

function checkInput() {
  let errors = false;
  let message = "The following issues have been found:\n";
  let type = $('#expType').val();

  let name = $("input[name=name]").val();
  if (name.length === 0 || !/\S/.test(name)) {
    errors = true;
    message += " - Name must not be empty\n";
  }

  let testcases = $("input[name=" + type + "_testCases]:checked").length;
  if (testcases === 0) {
    errors = true;
    message += " - Select at least one TestCase\n";
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

  if (checkBox.checked == true) {
    sliceList.removeAttribute("disabled");
  } else {
    sliceList.setAttribute("disabled", true);
  }
};

function changeSettingsDiv() {
  let type = $('#expType').val();
  $(".settingsDiv").hide();
  $("#"+type+"Settings").show();
}