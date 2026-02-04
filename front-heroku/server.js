const express = require("express");
const path = require("path");

const app = express();

const STATIC_DIR = path.join(__dirname, "front");
app.use(express.static(STATIC_DIR));

app.get("*", (req, res) => {
    res.sendFile(path.join(STATIC_DIR, "index.html"));
});

const port = process.env.PORT || 3000;
app.listen(port, "0.0.0.0", () => {
    console.log("Front on port", port);
});
