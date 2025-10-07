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

app.get("/api/login", (req, res) => {
  valid_sessionId = generateSessionId();
  console.log("Request /api/login: GenareateSessionId", valid_sessionId);
  res.cookie("sessionId", valid_sessionId, { httpOnly: true, secure: true });
  res.redirect("/");
});

app.get("/api/check_auth", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /api/check_auth: CurrentSessionId",
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
        league_key: "466.l.25038",
        league_id: "25038",
        name: "Hupu Alpha 2025-2026",
        url: "https://basketball.fantasysports.yahoo.com/nba/25038",
        logo_url: "https://s.yimg.com/ep/cx/blendr/v2/image-backboard-png_1721241478475.png",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "head",
        current_date: "2025-10-21",
        start_date: "2025-10-21",
        end_date: "2026-04-12",
        current_week: 1,
        start_week: "1",
        end_week: "24"
      },
      {
        league_key: "466.l.35424",
        league_id: "35424",
        name: "Star Basketball Association",
        url: "https://basketball.fantasysports.yahoo.com/nba/35424",
        logo_url: "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/67c5dbdd01aceece878642155459275a885462bc166ad53f07760f03570f111c.jpg",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "head",
        current_date: "2025-10-21",
        start_date: "2025-10-21",
        end_date: "2026-04-05",
        current_week: 1,
        start_week: "1",
        end_week: "23"
      },
      {
        league_key: "466.l.161296",
        league_id: "161296",
        name: "【九麦竞价】25-26 天玑盟",
        url: "https://basketball.fantasysports.yahoo.com/nba/161296",
        logo_url: "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/07343414b68755c9a19b3eab151a900bf6f8c917fe9cf9b2fff7de46e49256d8.png",
        draft_status: "predraft",
        num_teams: 16,
        scoring_type: "head",
        current_date: "2025-10-21",
        start_date: "2025-10-21",
        end_date: "2026-03-29",
        current_week: 1,
        start_week: "1",
        end_week: "22"
      },
      {
        league_key: "466.l.184111",
        league_id: "184111",
        name: "Beta 2025-26",
        url: "https://basketball.fantasysports.yahoo.com/nba/184111",
        logo_url: false,
        draft_status: "predraft",
        num_teams: 15,
        scoring_type: "roto",
        current_date: "2025-10-21",
        start_date: "2025-10-21",
        end_date: "2026-04-12",
        current_week: 1,
        start_week: "1",
        end_week: null
      }
    ] );
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
    const index = getDataCalled % resp_data_array.length;
    getDataCalled++;

    let resp_data = resp_data_array[index];
    const code = index  === resp_data_array.length - 1 ? 200 : 202;
      res.status(code).json(resp_data);
  } else {
    res.status(401).json({ authenticated: false });
  }
});

app.listen(port, () => {
  console.log(`Mock server listening at http://localhost:${port}`);
});
