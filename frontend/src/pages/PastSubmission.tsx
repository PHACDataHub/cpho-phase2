import { VStack, Text, Box, Heading } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { Page } from "./Page";

export function PastSubmissions() {
  const [indicators, setIndicators] = useState();

  useEffect(() => {
    fetch(
      process.env.REACT_APP_SERVER_URL ||
        "http://localhost:8000/api/pastsubmissions",
      {
        method: "GET",
      }
    )
      .then(async (res) => {
        const obj = await res.json();
        console.log(obj);
        if (obj.status === "resolved") {
          console.log("Got indicators");
        }
      })
      .catch((err) => {
        console.log("ERROR", err);
      });
  }, []);
  return (
    <Page
      title="Past Submissions"
      backButton={{ show: true, redirectUrl: "/" }}
    >
      {indicators}
    </Page>
  );
}
