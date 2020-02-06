let phone

$(document).ready(function(){
  $('.ui.dropdown').dropdown();  
  refreshVoteCounts()
  document.getElementsByClassName("ui green button")[0].addEventListener("click", voteForSong);
  document.getElementsByClassName("ui purple button")[0].addEventListener("click", generateCode);
});

var endpoint_url_root = "REPLACE_ME"
var vote_endpoint = endpoint_url_root + "/song/vote"
var get_votes_endpoint = endpoint_url_root + "/votes"
var generate_code_endpoint = endpoint_url_root + "/send-code"

async function generateCode() {
  phoneNumber = document.getElementById("phoneNumber").value
  var sentDialog = document.getElementById("sentDialog").innerHTML
  if (phoneNumber && sentDialog != "Sending you a code...") {
    document.getElementById("sentDialog").innerHTML = "Sending you a code..."
    phone = phoneNumber
    const response = await fetch(generate_code_endpoint, {
      method: "POST",
      mode: 'cors',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({"phoneNumber": phoneNumber})
    })
    result_json = await response.json()
    document.getElementById("sentDialog").innerHTML = result_json["status"]
  }
}

function setVotes(songName, voteCount) {
  // Get div containing vote count and set the new voteCount
  document.getElementsByName(songName)[0].innerHTML = voteCount;
}

async function refreshVoteCounts() {
  // Get the vote counts
  const response = await fetch(get_votes_endpoint);
  const songs = await response.json();
  // Iterate over all three songs and update the divs
  var i;
  for (i = 0; i < songs.length; i++){
    var featured_songs = ["coderitis", "stateless", "dynamo"];
    var song = songs[i]
    if (featured_songs.includes(song["songName"])){
      console.log(song)
      setVotes(song["songName"], song["votes"])
    }
  }
}

async function voteForSong() {
  if (document.getElementsByClassName("item active selected")[0]) {
    var songName = document.getElementsByClassName("item active selected")[0].getAttribute('data-value')
  }
  if (document.getElementById("verificationCode").value) {
    var verificationCode = document.getElementById("verificationCode").value
  }
  if (songName && verificationCode) {
    const response = await fetch(vote_endpoint, {
      method: "POST",
      mode: 'cors',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        "songName": songName, 
        "verificationCode": verificationCode,
        "phoneNumber": phone
      })
    })
    const result_json = await response.json()
    if (result_json.hasOwnProperty("votes")){
      setVotes(songName, result_json["votes"])
    } 
    if (result_json.hasOwnProperty("status")){
      document.getElementById("sentDialog").innerHTML = result_json["status"]
    }
  }
}
