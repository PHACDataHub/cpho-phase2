import { Flex } from "@chakra-ui/react";
import { useSmallScreen } from "../utils/hooks";
import IndicatorForm from "./components/addIndicatorForm/IndicatorForm";
import { Page } from "./Page";

export function AddIndicator() {
  const smallScreen = useSmallScreen();

  return (
    <Page backButton={{ show: true, redirectUrl: "/" }} title="Add Indicator">
      <Flex
        w={smallScreen ? "95%" : "90%"}
        margin="auto"
        justify="space-around"
        align="flex-start"
      >
        <IndicatorForm />
      </Flex>
    </Page>
  );
}
