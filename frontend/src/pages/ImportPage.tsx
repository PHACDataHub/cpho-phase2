import { VStack, Text, Box } from "@chakra-ui/react";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { Page } from "./Page";

export function ImportPage() {
  return (
    <Page
      title="Import File"
      backButton={{ show: true, redirectUrl: "/" }}
    ></Page>
  );
}
