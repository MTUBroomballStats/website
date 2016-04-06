<?php
if ($_GET['randomId'] != "nb6vmsp7cb_JDsHkfFzqzG5AReUCNroKhlvQuCnxZllzjDVPKjJFr2Q_n7mFEemS") {
    echo "Access Denied";
    exit();
}

// display the HTML code:
echo stripslashes($_POST['wproPreviewHTML']);

?>  
