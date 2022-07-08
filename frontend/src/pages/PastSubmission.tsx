import { VStack, Text, Box, Heading } from "@chakra-ui/react";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { Page } from "./Page";

export function PastSubmissions() {
  return (
    <Page
      title="Past Submissions"
      backButton={{ show: true, redirectUrl: "/" }}
    ></Page>
  );
}
