# [Error Handling](#error-handling){.header}

In this chapter, we will explain how error handling is designed and implemented in our MAX7219 driver using Rust\'s enum and traits. All these related code goes inside the error.rs module.

During interaction with this chip, many things can fail:

- The user might configure an invalid number of devices.

- The driver might receive invalid commands or indices.

- SPI communication can fail due to hardware issues.

## [Defining the Error Enum](#defining-the-error-enum){.header}

We define a custom Error enum that lists all the possible errors the driver can produce:

    #![allow(unused)]
    fn main() {
    #[derive(Debug, PartialEq, Eq)]
    pub enum Error {
        /// The specified device count is invalid (exceeds maximum allowed).
        InvalidDeviceCount,
        /// Invalid scan limit value (must be 0-7)
        InvalidScanLimit,
        /// The specified register address is not valid for the MAX7219.
        InvalidRegister,
        /// Invalid device index (exceeds configured number of devices)
        InvalidDeviceIndex,
        /// Invalid digit position (0-7 for MAX7219)
        InvalidDigit,
        /// Invalid intensity value (must be 0-15)
        InvalidIntensity,
        /// SPI communication error
        SpiError,
    }
    }

## [Converting SPI Errors into Our Driver Error](#converting-spi-errors-into-our-driver-error){.header}

The MAX7219 driver communicates over SPI, which may produce errors defined by the SPI implementation. To unify error handling, we implement From for our Error where E is any embedded-hal SPI error:

    #![allow(unused)]
    fn main() {
    impl<E> From<E> for Error
    where
        E: embedded_hal::spi::Error,
    {
        fn from(_value: E) -> Self {
            Self::SpiError
        }
    }
    }

This lets us use the ? operator with SPI calls inside the driver, automatically converting any SPI-specific error into the driver\'s SpiError variant. It simplifies error propagation and keeps our API consistent.

## [Implementing Display for User-Friendly Messages](#implementing-display-for-user-friendly-messages){.header}

To make errors easier to read and understand, we implement the Display trait for our Error enum. This allows errors to be formatted as human-friendly strings, useful for logging or debugging:

    #![allow(unused)]
    fn main() {
    impl core::fmt::Display for Error {
        fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
            match self {
                Self::SpiError => write!(f, "SPI communication error"),
                Self::InvalidDeviceIndex => write!(f, "Invalid device index"),
                Self::InvalidDigit => write!(f, "Invalid digit"),
                Self::InvalidIntensity => write!(f, "Invalid intensity value"),
                Self::InvalidScanLimit => write!(f, "Invalid scan limit value"),
                Self::InvalidDeviceCount => write!(f, "Invalid device count"),
                Self::InvalidRegister => write!(f, "Invalid register address"),
            }
        }
    }
    }

## [Update lib.rs](#update-librs){.header} {#update-librs}

To simplify function signatures throughout the driver, we define a crate-local Result type alias that defaults the error type to our custom Error:

    #![allow(unused)]
    fn main() {
    pub(crate) type Result<T> = core::result::Result<T, crate::error::Error>;
    }

This lets us write all function signatures using just Result, making the code cleaner and easier to read.

Instead of writing:

    #![allow(unused)]
    fn main() {
    fn set_intensity(intensity: u8) -> core::result::Result<(), crate::error::Error> {
        //..
    }
    }

we can simply write:

    #![allow(unused)]
    fn main() {
    fn set_intensity(intensity: u8) -> Result<()> {
        // ...
    }
    }
