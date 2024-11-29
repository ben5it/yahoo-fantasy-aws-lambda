import express from "express";
import cookieParser from "cookie-parser";
import resp_data_array from "./mock-data.js";

const app = express();
const port = 3001;

// Middleware to parse JSON request bodies and cookies
app.use(express.json());
app.use(cookieParser());

// In-memory storage for demonstration purposes

let valid_sessionId = null;

let getDataCalled = 0;

// Helper function to generate a random session ID
const generateSessionId = () => Math.random().toString(36).substring(2, 15);

app.get("/login", (req, res) => {
  valid_sessionId = generateSessionId();
  console.log("Request /login: GenareateSessionId", valid_sessionId);
  res.cookie("sessionId", valid_sessionId, { httpOnly: true, secure: true });
  res.redirect("/");
});

app.get("/check_auth", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /check_auth: CurrentSessionId",
    sessionId,
    "ValidSessionId",
    valid_sessionId
  );
  if (sessionId === valid_sessionId) {
    res.json({
      authenticated: true,
      user_info: {
        userId: "EQMHXVGZ65XDJ5G57ZRRBKXUTM",
        email: "husthsz@yahoo.com",
        nickname: "邪",
        profile_image:
          "https://s.yimg.com/ag/images/c58ba041-8d68-4d15-91ac-56dde65c1c9fqV_32sq.jpg",
      },
    });
  } else {
    res.json({ authenticated: false });
  }
});

app.get("/api/leagues", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /api/leagues: CurrentSessionId",
    sessionId,
    "ValidSessionId",
    valid_sessionId
  );
  if (sessionId === valid_sessionId) {
    res.json([
      {
        league_key: "454.l.29689",
        league_id: "29689",
        name: "Hupu Alpha 2024-2025",
        url: "https://basketball.fantasysports.yahoo.com/nba/29689",
        logo_url:
          "https://s.yimg.com/ep/cx/blendr/v2/image-y-png_1721252122724.png",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "head",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
        current_week: 6,
        start_week: "1",
        end_week: "23",
      },
      {
        league_key: "454.l.35674",
        league_id: "35674",
        name: "Star Basketball Association",
        url: "https://basketball.fantasysports.yahoo.com/nba/35674",
        logo_url:
          "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/67c5dbdd01aceece878642155459275a885462bc166ad53f07760f03570f111c.jpg",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "head",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
        current_week: 6,
        start_week: "1",
        end_week: "23",
      },
      {
        league_key: "454.l.38297",
        league_id: "38297",
        name: "HUPU BETA 2024-2025",
        url: "https://basketball.fantasysports.yahoo.com/nba/38297",
        logo_url:
          "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/132d3d075691e9503531915c083b69512150bbbdd0ac0cc9c961fa7847f7d2b6.jpg",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "roto",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
      },
      {
        league_key: "454.l.68157",
        league_id: "68157",
        name: "Never Ending",
        url: "https://basketball.fantasysports.yahoo.com/nba/68157",
        logo_url:
          "https://s.yimg.com/ep/cx/blendr/v2/image-basketball-3-png_1721241401648.png",
        draft_status: "predraft",
        num_teams: 15,
        scoring_type: "head",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
        current_week: 6,
        start_week: "1",
        end_week: "23",
      },
    ]);
  } else {
    res.status(401).json({ error: "Unauthorized" });
  }
});


app.get("/api/getdata", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /getdata: CurrentSessionId",
    sessionId,
    "ValidSessionId",
    valid_sessionId
  );
  if (sessionId === valid_sessionId) {
    let resp_data = resp_data_array[getDataCalled++ % 5];
      res.json(resp_data);
  } else {
    res.json({ authenticated: false });
  }
});

app.listen(port, () => {
  console.log(`Mock server listening at http://localhost:${port}`);
});
