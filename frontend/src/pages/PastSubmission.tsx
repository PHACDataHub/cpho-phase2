import { VStack, Text, Spinner } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { Page } from "./Page";

export function PastSubmissions() {
  const [indicators, setIndicators] = useState([]);

  useEffect(() => {
    fetch(
      (process.env.REACT_APP_SERVER_URL || "http://localhost:8000/") +
        "api/pastsubmissions",
      {
        method: "GET",
      }
    )
      .then(async (res) => {
        const obj = await res.json();
        setIndicators(obj);
        console.log(obj);
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
      <VStack>
        {indicators ? (
          indicators.map(({ id, indicator }) => (
            <Text key={id}>{indicator}</Text>
          ))
        ) : (
          <Spinner />
        )}
      </VStack>
    </Page>
  );
}
