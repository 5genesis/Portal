$(document).ready(
  function() {
    $('#checkBtn').click(function() {
      checked = $("input[name=testCases]:checked").length;
      if (!checked) {
        alert("Please, select at least one Test Case");
        return false;
      }
    });
  }
);

function addNs(actual, target, nss, nsIds) {
  for (i = actual + 1; i <= target; i++) {
    newItemHTML = '<tr><td class="table-cell-divisor-right"><center>' + i + '</center></td><td class="table-cell-divisor-right"><select class="ns InputBox form-control" name="NS' + i + '">'
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
  var checkBox = document.getElementById('sliceNone');
  var sliceList = document.getElementById('sliceList');

  if (checkBox.checked == true) {
    sliceList.removeAttribute("disabled");
  } else {
    sliceList.setAttribute("disabled", true);
  }
};