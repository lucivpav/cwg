var id;
const URL = "http://127.0.0.1:5002";
const GENERATOR_UNAVAILABLE_MSG = "Generator is unavailable. Please try again later.";
const SERVER_FUCKED_UP_MSG = "Failed to generate sheet. Please enter different configuration or try again later.";

function generateInfos()
{
  document.getElementById("infos_loading").style.display = "inline";
  document.getElementById("infos_error").style.display = "none";
  var characters = document.getElementById("characters").value;
  var title = document.getElementById("title").value;
  var guide = document.getElementById("guide").value;

  var url = URL + "/generate_infos?characters=" + characters;
  var req = new XMLHttpRequest();
  req.open("GET", url, true);
  req.onload = function (e) {
    if ( req.readyState === 4 ) {
      if ( req.status === 200 ) {
        response = JSON.parse(req.responseText);
        onInfosGenerated(response);
      } else {
        showError("infos_error", SERVER_FUCKED_UP_MSG);
      }
      document.getElementById("infos_loading").style.display = "none";
    }
  }
  req.onerror = function (e) {
    document.getElementById("infos_loading").style.display = "none";
    showError("infos_error", GENERATOR_UNAVAILABLE_MSG);
  }
  req.send(null);
}

function onInfosGenerated(response)
{
  if ( response.hasOwnProperty("error") )
  {
    showError("infos_error", response["error"]);
    return;
  }
  createCharactersTable(response["infos"]);
  document.getElementById("confirm").style.display = "inline";
  id = response["id"];
}

function createCharactersTable(infos)
{
  var table = '<div class="table-responsive"><table class="table" id="actual_characters_table"><thead><tr><th>Character</th><th>Pinyin</th><th>Definition</th></tr></thead><tbody>';
  for (i = 0 ; i < infos.length ; i++)
  {
    row = '<tr><td class="narrow"><input type="text" class="form-control input-lg" value="' + infos[i].character + '" disabled></td>' + 
      '<td class="narrow"><input type="text" id="pinyin' + i + '" class="form-control input-lg" value="' + infos[i].pinyin + '"></td>' +
      '<td class="wide"><input type="text" id="definition' + i + '" class="form-control input-lg" value="' + infos[i].definition + '"></td></tr>';
    table += row;
  }
  table += '</tbody></table></div>';
  document.getElementById("characters_table").innerHTML = table;
}

function generateSheet()
{
  var title = document.getElementById("title").value;
  var guide = document.getElementById("guide").value;
  if ( guide == 0 )
    guide = "none";
  else if ( guide == 1 )
    guide = "star";
  else
  {
    showError("sheet_error", "Invalid guide selected.");
    return;
  }
  var url = URL + "/generate_sheet?id=" + id +
            "&guide=" + guide +
            "&title=" + title;
  var n = document.getElementById("actual_characters_table").rows.length-1;
  for ( i = 0 ; i < n ; i++ )
  {
    var pinyin = document.getElementById("pinyin" + i).value;
    var definition = document.getElementById("definition" + i).value;
    url += "&pinyin" + i + "=" + pinyin;
    url += "&definition" + i + "=" + definition;
  }

  var req = new XMLHttpRequest();
  req.open("GET", url, true);
  req.onload = function (e) {
    if ( req.readyState === 4 ) {
      if ( req.status === 200 ) {
        response = JSON.parse(req.responseText);
        onSheetGenerated(response);
      } else {
        showError("sheet_error", SERVER_FUCKED_UP_MSG);
      }
      document.getElementById("sheet_loading").style.display = "none";
    }
  }
  req.onerror = function (e) {
    document.getElementById("sheet_loading").style.display = "none";
    showError("sheet_error", GENERATOR_UNAVAILABLE_MSG);
  }
  document.getElementById("sheet_loading").style.display = "inline";
  req.send(null);
}

function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', window.URL.createObjectURL(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function retrieveSheet()
{
  var url = URL + "/retrieve_sheet?id=" + id;
  var req = new XMLHttpRequest();
  req.open("GET", url, true);
  req.responseType = "blob";
  req.onload = function (e) {
    if ( req.readyState === 4 ) {
      if ( req.status === 200 ) {
        response = req.response;
        download("worksheet.pdf", response);
      } else {
        showError("retrieve_error", SERVER_FUCKED_UP_MSG);
      }
    }
  }
  req.onerror = function (e) {
    showError("retrieve_error", GENERATOR_UNAVAILABLE_MSG);
  }
  req.send(null);
}

function onSheetGenerated(response)
{
  if ( response.hasOwnProperty("error") )
  {
    showError("sheet_error", response["error"]);
    return;
  }
  document.getElementById("download").style.display = "inline";
}

function showError(element, message)
{
  document.getElementById(element).style.display = "inline";
  document.getElementById(element).innerHTML = "<strong>Error: </strong>" + message;
}
