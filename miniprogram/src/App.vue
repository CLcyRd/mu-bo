<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { refreshAuthState } from "./utils/auth";
onLaunch(() => {
  refreshAuthState();
});
onShow(() => {
  refreshAuthState();
});
onHide(() => {
  console.log("App Hide");
});
</script>
<style></style>
