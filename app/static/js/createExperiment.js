

function checkInput() {
  checked = $("input[name=testCases]:checked").length;
  if (!checked) {
    alert("Please, select at least one Test Case");
    return false;
  }
  return true;
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
  console.log(type);
  $(".settingsDiv").hide();
  $("#"+type+"Settings").show();
}