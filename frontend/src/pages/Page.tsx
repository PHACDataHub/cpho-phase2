import { VStack, Heading, Box, Button } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { Footer } from "./components/common/Footer";
import { Header } from "./components/common/Header";

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
    <Box minHeight="100vh" display="flex" flexDir="column">
      <Header />
      <hr
        style={{
          marginTop: 10,
          marginBottom: 10,
        }}
      />
      <Box p={5}>
        {backButton && backButton.show && (
          <Button onClick={() => navigate(backButton.redirectUrl)}>Back</Button>
        )}
        <VStack spacing={3} align="flex-start" p={5}>
          <Heading fontWeight={700} size="xl">
            {title}
          </Heading>
          {subTitle && (
            <Heading fontWeight={500} size="md">
              {subTitle}
            </Heading>
          )}
        </VStack>
        <Box px={5}>{children}</Box>
      </Box>
      <Footer />
    </Box>
  );
}
