# `refill-controller` module

This [module](https://docs.viam.com/registry/modular-resources/) implements the [`rdk:service:generic` API](https://docs.viam.com/appendix/apis/services/generic/) for the Smart Snack Dispenser demo.

With this model, you can set up automated refilling of a snack bowl from a motorized dispenser using computer vision.

## Requirements

This module assumes you have a Viam machine configured with a camera component, a motor component, and a vision service that can perform image classification.

## Model: viam-demo:refill-controller:refiller

With this model, you can set up automated refilling of a snack bowl from a motorized dispenser using computer vision.

Navigate to the [**CONFIGURE** tab](https://docs.viam.com/configure/) of your [machine](https://docs.viam.com/fleet/machines/) in the [Viam app](https://app.viam.com/).
[Add `viam-demo:refill-controller` to your machine](https://docs.viam.com/configure/#services).

### Attributes

The following attributes are available for `viam-demo:refill-controller:refiller` generic service:

| Name    | Type   | Required?    | Default | Description |
| ------- | ------ | ------------ | ------- | ----------- |
| `camera_name` | string | Required | N/A | The name of the camera component to use to get images. |
| `motor_name` | string | Required | N/A | The name of the motor component to use to dispense snacks. |
| `vision_name` | string | Required | N/A | The name of the vision service to use to get classifications using the image from the camera. |
| `confidence_level` | number | Optional | 0.55 | Number between 0 and 1 as a minimum percentage of confidence for the returned classifications from the vision service. |
| `auto_start` | boolean | Optional | true | Set the control loop to automatically start when the machine is powered on. |

### Example configuration

```json
{
    "camera_name": "camera-1",
    "motor_name": "motor-1",
    "vision_name": "vision-1"
}
```

## Commands

This module implements the following commands to be used by the `DoCommand` method in the Control tab of the Viam app or one of the language SDKs.

**start**

Start the control loop for detecting an empty bowl and triggering refills.

```json
{
    "start": []
}
```

**stop**

Stop the control loop.

```json
{
    "stop": []
}
```
