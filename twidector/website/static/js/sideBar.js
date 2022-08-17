$(function () {
  $("#sidebarCollapse").on("click", function () {
    $("#sidebar, #content").toggleClass("active");
  });
});

function openNav() {
  document.getElementById("sidebar").style.width = "250px";
}