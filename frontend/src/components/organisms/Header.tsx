import { HStack, Image, useColorMode } from "@chakra-ui/react";
import { ColorModeSwitcher } from "../../ColorModeSwitcher";
import { Phacsignature } from "../atoms/Phacsignature";

export function Header(): JSX.Element {
  const { colorMode } = useColorMode();

  return (
    <>
      <HStack w="100%" display="flex" justify="space-between" p={5}>
        <Image maxWidth="400px" width="80%" src="/static/images/logo.svg" />
        

        {/* TODO: Implement language switcher */}
        <ColorModeSwitcher />

      </HStack>
      
      <Phacsignature
          textColor={colorMode === "dark" ? "white" : "black"}
          variant="color"
          
        />
      <hr
        style={{
          marginTop: 10,
          marginBottom: 10,
        }}
      />
    </>
  );
}
