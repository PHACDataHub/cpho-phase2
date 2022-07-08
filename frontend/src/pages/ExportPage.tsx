import { VStack, Text, Box } from "@chakra-ui/react";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { Page } from "./Page";

export function ExportPage() {
  return (
    <Page
      title="Export Data"
      backButton={{ show: true, redirectUrl: "/" }}
    ></Page>
  );
}
