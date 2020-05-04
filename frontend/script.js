var id;

const BASE_URL = "http://127.0.0.1"
const URL = BASE_URL + ":5002";
const GENERATOR_UNAVAILABLE_MSG = "Generator is unavailable. Please try again later.";
const SERVER_FUCKED_UP_MSG = "Failed to generate sheet. Please enter different configuration or try again later.";

function onLoad()
{
  document.getElementById("home_link").href = BASE_URL;
  var url = URL + "/retrieve_count";
  var req = new XMLHttpRequest();
  req.open("GET", url, true);
  req.onload = function (e) {
    if ( req.readyState === 4 ) {
      if ( req.status === 200 ) {
        response = JSON.parse(req.responseText);
        count = response["count"];
        text = "Number of worksheets generated: " + count;
        document.getElementById("worksheets_generated").innerHTML = text;
      }
    }
  }
  req.send(null);
}

function generateInfos()
{
  document.getElementById("infos_loading").style.display = "inline";
  document.getElementById("infos_error").style.display = "none";
  document.getElementById("sheet_loading").style.display = "none";
  document.getElementById("sheet_error").style.display = "none";
  document.getElementById("retrieve_error").style.display = "none";
  document.getElementById("characters_table").style.display = "none";
  document.getElementById("words_table").style.display = "none";
  document.getElementById("confirm").style.display = "none";
  document.getElementById("download").style.display = "none";
  var characters = document.getElementById("characters").value;
  var title = getWorksheetTitle();
  var guide = document.getElementById("guide").value;

  var url = URL + "/generate_infos";
  var req = new XMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader("Content-Type", "application/json");

  req.onreadystatechange = function () { //Call a function when the state changes.

    if (req.readyState === 4 && req.status === 200) {
        response = JSON.parse(req.responseText);
        onInfosGenerated(response);
    } 

    document.getElementById("infos_loading").style.display = "none";
  }
  scharacters = { "characters": characters }
  req.onerror = function (e) {
    document.getElementById("infos_loading").style.display = "none";
    showError("sheet_error", GENERATOR_UNAVAILABLE_MSG + ": " + e) ;
  }
  document.getElementById("infos_loading").style.display = "inline";
  req.send(JSON.stringify(scharacters));
}

function onInfosGenerated(response)
{
  if ( response.hasOwnProperty("error") )
  {
    showError("infos_error", response["error"]);
    return;
  }
  createCharactersTable(response["characters"]);
  createWordsTable(response["words"]);
  document.getElementById("confirm").style.display = "inline";
  id = response["id"];
  // console.log("id: " + id)
}

function createCharactersTable(infos)
{
  var table = '<div class="table-responsive"><table class="table" id="actual_characters_table"><thead><tr><th>Character</th><th>Pinyin</th><th>Definition</th></tr></thead><tbody>';
  for (i = 0 ; i < infos.length ; i++)
  {
    row = '<tr><td class="narrow"><input type="text" id="character' + i + '" class="form-control input-lg" value="' + infos[i].character + '" disabled></td>' + 
      '<td class="narrow"><input type="text" id="pinyin' + i + '" class="form-control input-lg" value="' + infos[i].pinyin + '"></td>' +
      '<td class="wide"><input type="text" id="definition' + i + '" class="form-control input-lg" value="' + infos[i].definition + '"></td></tr>';
    table += row;
  }
  table += '</tbody></table></div>';
  document.getElementById("characters_table").innerHTML = table;
  document.getElementById("characters_table").style.display = "inline";
}

function createWordsTable(words)
{
  if ( words.length == 0 )
    return;
  var table = '<div class="table-responsive"><table class="table" id="actual_words_table"><thread><tr><th>Word</th><th>Definition</th></tr></thead><tbody>';
  for (i = 0 ; i < words.length ; i++)
  {
    row = '<tr><td class="narrow"><input type="text" class="form-control input-lg" value="' + words[i].characters + '" disabled></td>' +
      '<td class="wide"><div class="form-inline"><input type="text" id="word_definition' + i + '" class="form-control input-lg tm-input tm-input-large"></div></td></tr>';
    table += row;
  }
  table += '</tbody></table></div>';
  document.getElementById("words_table").innerHTML = table;
  document.getElementById("words_table").style.display = "inline";

  $(".tm-input").tagsManager();

  // add word tags
  for (i = 0 ; i < words.length ; i++)
  {
    for (j in words[i].definition)
      $("#word_definition" + i).tagsManager('pushTag', words[i].definition[j]);
  }
}

function generateSheet()
{
  document.getElementById("sheet_error").style.display = "none";
  document.getElementById("download").style.display = "none";
  var title = getWorksheetTitle();
  var guide = document.getElementById("guide").value;
  var payload = {};
  if ( guide == 0 )
    guide = "none";
  else if ( guide == 1 )
    guide = "star";
  else if ( guide == 2 )
    guide = "cross";
  else if ( guide == 3 )
    guide = "cross_star";
  else
  {
    showError("sheet_error", "Invalid guide selected.");
    return;
  }
  var url = URL + "/generate_sheet?id=" + id +
            "&guide=" + guide +
            "&title=" + title;
  payload.id = id;
  payload.guide = guide;
  payload.title = title;
  
  payload.characters = get_character_parameters();
  payload.words = get_words_parameters();
  var req = new XMLHttpRequest();
  req.open("POST", url, true);
  req.setRequestHeader("Content-Type", "application/json");
  req.onreadystatechange = function () {
  if (req.readyState === 4 && req.status === 200) {
        response = JSON.parse(req.responseText);
        onSheetGenerated(response);
    } 
    document.getElementById("sheet_loading").style.display = "none";
  }
  req.onerror = function (e) {
    document.getElementById("sheet_loading").style.display = "none";
    showError("sheet_error", GENERATOR_UNAVAILABLE_MSG) ;
  }
  document.getElementById("sheet_loading").style.display = "inline";
  req.send(JSON.stringify(payload));
}

function get_character_parameters() {
  var charparams = {};
  var n = document.getElementById("actual_characters_table").rows.length-1;
  for ( i = 0 ; i < n ; i++ )
  {
    var character = document.getElementById("character" + i).value;
    var pinyin = document.getElementById("pinyin" + i).value;
    var definition = document.getElementById("definition" + i).value;
    charparams[character] = {};
    charparams[character].pinyin = pinyin;
    charparams[character].definition = definition;
  }
  return charparams;
}

function get_words_parameters() {
  var worddefs = [];
  var wt = document.getElementById("actual_words_table");
  if ( wt == null ) return worddefs;
  n = wt.rows.length-1;
  for ( i = 0 ; i < n ; i++ )
  {
    var tags = $("#word_definition" + i).tagsManager('tags');
    worddefs.push(tags);

  }
  return worddefs;
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

function getWorksheetTitle() {
  return document.getElementById("title").value;
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

        filename = getWorksheetTitle()
        if (filename == "") {
          filename = "worksheet";
        }
        filename += ".pdf";

        download(filename, response);
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
