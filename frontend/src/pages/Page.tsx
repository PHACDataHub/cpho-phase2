import { VStack, Heading, Box, Button } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";

export function Page({
  title,
  subTitle,
  children,
  backButton,
}: {
  title: String;
  subTitle?: String;
  children?: any;
  backButton?: {
    show: boolean;
    redirectUrl: string;
  };
}) {
  let navigate = useNavigate();
  return (
    <Box textAlign="center">
      <VStack backgroundColor={"red.200"} py={10} spacing={8}>
        {backButton && backButton.show && (
          <Button onClick={() => navigate(backButton.redirectUrl)}>Back</Button>
        )}
        <Heading size="2xl">{title}</Heading>
        {subTitle && <Heading size="lg">{subTitle}</Heading>}
      </VStack>
      <>{children}</>
    </Box>
  );
}
