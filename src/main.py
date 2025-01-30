import asyncio
from threading import Event
from typing import ClassVar, List, Mapping, Optional, Sequence, cast

from typing_extensions import Self
from viam.components.camera import Camera
from viam.components.motor import Motor
from viam.proto.service.vision import Classification
from viam.services.vision import Vision
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.generic import Generic
from viam.logging import getLogger
from viam.utils import struct_to_dict, ValueTypes

LOGGER = getLogger("refill-controller")


class Refiller(Generic, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("viam-demo", "refill-controller"), "refiller"
    )

    task = None
    event = Event()
    auto_start = False
    rpm = 60
    rev = 10

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic service.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        attrs = struct_to_dict(config.attributes)

        camera_name, motor_name, vision_name = (
            attrs.get("camera_name"),
            attrs.get("motor_name"),
            attrs.get("vision_name"),
        )

        if camera_name is None:
            raise Exception("Missing required camera_name attribute.")

        if motor_name is None:
            raise Exception("Missing required motor_name attribute.")

        if vision_name is None:
            raise Exception("Missing required vision_name attribute.")

        return [str(camera_name), str(motor_name), str(vision_name)]

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        attrs = struct_to_dict(config.attributes)

        camera_resource = dependencies.get(
            Camera.get_resource_name(str(attrs.get("camera_name")))
        )
        self.camera = cast(Camera, camera_resource)

        motor_resource = dependencies.get(
            Motor.get_resource_name(str(attrs.get("motor_name")))
        )
        self.motor = cast(Motor, motor_resource)

        vision_resource = dependencies.get(
            Vision.get_resource_name(str(attrs.get("vision_name")))
        )
        self.vision = cast(Vision, vision_resource)

        self.confidence_level = float(attrs.get("confidence_level", 0.55))

        if self.auto_start:
            self.start()

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.control_loop())
        self.event.clear()

    def stop(self):
        self.event.set()
        if self.task is not None:
            self.task.cancel()

    async def control_loop(self):
        while not self.event.is_set():
            await self.on_loop()
            await asyncio.sleep(0)

    async def on_loop(self):
        try:
            for _ in range(0, 3):
                await self.camera.get_image()
            image = await self.camera.get_image()

            classifications = await self.vision.get_classifications(image, 1)

            if len(classifications) == 0:
                LOGGER.debug("No classifications found.")

            should_refill = await self.handle_classification(classifications)
            if should_refill:
                LOGGER.info("Refill required")
                await self.motor.go_for(self.rpm, self.rev)

            await asyncio.sleep(10)
        except Exception as err:
            LOGGER.error(err)

    async def handle_classification(
        self, classifications: List[Classification]
    ) -> bool:
        for classification in classifications:
            if (
                classification.class_name == "empty"
                and classification.confidence > self.confidence_level
            ):
                return True
        return False

    def __del__(self):
        self.stop()

    async def close(self):
        self.stop()

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        result = {key: False for key in command.keys()}
        for name, _args in command.items():
            if name == "start":
                self.start()
                result[name] = True
            if name == "stop":
                self.stop()
                result[name] = True
        return result


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
