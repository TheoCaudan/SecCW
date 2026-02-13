#!/usr/bin/env python
import numpy as np
import pyfftw
import matplotlib.pyplot as plt
import sys
import gc
import argparse
import os

def read_img_real(input_file, save=False, prefix=""):
    try:
        data = np.memmap(input_file, dtype=np.int8, mode='r')
        real = data[0::2]
        imag = data[1::2]
        step = max(1, len(real) // 2000)
        
        plt.figure(figsize=(10, 4))
        plt.plot(real[::step], label="Real part (sample)", color="blue")
        plt.title("Real part - Baseband signal")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.legend(loc="upper right")
        plt.grid(True)
        
        if save:
            out = f"{prefix}real.png"
            plt.savefig(out, dpi=150, bbox_inches="tight")
            print(f"[OUT] Figure saved : {out}")
            plt.close()
        else:
            plt.show()
            
        plt.figure(figsize=(10, 4))
        plt.plot(imag[::step], label="Imaginary part (sample)", color="red")
        plt.title("Imaginary part - Baseband signal")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.legend(loc="upper right")
        plt.grid(True)
        
        if save:
            out = f"{prefix}real.png"
            plt.savefig(out, dpi=150, bbox_inches="tight")
            print(f"[OUT] Figure saved : {out}")
            plt.close()
        else:
            plt.show()
            
        del data, real, imag
        gc.collect()
        
    except FileNotFoundError:
        print(f"[!] File {input_file} not found")
    except Exception as e:
        print(f"[!] Error (read_img_real):\n{str(e)}")
        
def read_fft(input_file, sampling_rate=48000, max_fft_samples=2**20, save=False, prefix=""):
    print("[OUT] FFT...")
    try:
        data = np.memmap(input_file, dtype=np.int8, mode='r')
        real = data[0::2].astype(np.float32)
        imag = data[1::2].astype(np.float32)
        iq_signal = real + 1j * imag
        
        n_samples = min(len(iq_signal), max_fft_samples)
        if len(iq_signal) > max_fft_samples:
            print(f"[OUT] FFT limited to {n_samples} samples on {len(iq_signal)}")
            
        iq_signal = iq_signal[:n_samples]
        
        optimal_size = 2**int(np.ceil(np.log2(n_samples)))
        if optimal_size > n_samples:
            iq_signal = np.pad(iq_signal, (0, optimal_size - n_samples), mode='constant')
            
        fft_in = pyfftw.empty_aligned(optimal_size, dtype='complex64')
        fft_out = pyfftw.empty_aligned(optimal_size, dtype='complex64')
        fft_in[:] = iq_signal.astype('complex64')
        
        fft_object = pyfftw.FFTW(fft_in, fft_out, threads=4)
        fft_result = fft_object()
        fft_shifted = np.fft.fftshift(fft_result)
        fft_magnitude = 20 * np.log10(np.maximum(np.abs(fft_shifted), 1e-12))
        
        freqs = np.linspace(-sampling_rate / 2, sampling_rate / 2, num=len(fft_magnitude))
        
        step = max(1, len(fft_magnitude) // 2000)
        
        plt.figure(figsize=(10, 5))
        plt.plot(freqs[::step], fft_magnitude[::step], label="Signal spectre (FFT)", color="green")
        plt.title("Frequency spectre (FFT)")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude (dB)")
        plt.legend(loc="upper right")
        plt.grid(True)
        
        if save:
            out = f"{prefix}fft.png"
            plt.savefig(out, dpi=150, bbox_inches="tight")
            print(f"[OUT] Figure saved : {out}")
            plt.close()
        else:
            plt.show()
            
        del data, real, imag, iq_signal, fft_in, fft_out, fft_result, fft_shifted, fft_magnitude, freqs
        gc.collect()
        
    except FileNotFoundError:
        print(f"[!] File {input_file} not found")
    except Exception as e:
        print(f"[!] Error (read_fft):\n{str(e)}")
        
def read_amplitude(input_file, sampling_rate=48000, save=False, prefix=""):
    print("[OUT] Amplitude vs Time...")
    try:
        data = np.memmap(input_file, dtype=np.int8, mode='r')
        real = data[0::2].astype(np.float32)
        imag = data[1::2].astype(np.float32)
        iq_signal = real + 1j * imag
        
        amplitude = np.abs(iq_signal)
        time = np.linspace(0, len(amplitude) / sampling_rate, num=len(amplitude))
        step = max(1, len(amplitude) // 40000)
        
        plt.figure(figsize=(10, 5))
        plt.plot(time[::step], amplitude[::step], label="Signal amplitude", color="purple")
        plt.title("Signal amplitude from Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.legend(loc="upper right")
        plt.grid(True)
        
        if save:
            out = f"{prefix}fft.png"
            plt.savefig(out, dpi=150, bbox_inches="tight")
            print(f"[OUT] Figure saved : {out}")
            plt.close()
        else:
            plt.show()
        
        del data, real, imag, iq_signal, amplitude, time
        gc.collect()
        
    except FileNotFoundError:
        print(f"[!] File {input_file} not found")
    except ValueError:
        print("[!] Error data type. Please check the file")
    except Exception as e:
        print(f"[!] Error (read_amplitude):\n{str(e)}")
        
def parse_args():
    parser = argparse.ArgumentParser(description="CS8 file analyze")
    parser.add_argument("input_file", help="CS8 file in input")
    parser.add_argument("--mode", choices=["amplitude", "fft", "iq", "all"], default="amplitude",
                        help="Display type: amplitude, fft, iq (real/imag), or all (default: amplitude)",)
    parser.add_argument("--sampling_rate", type=float, default=48000,
                        help="Sample rate in Hz (default: 48000)",)
    parser.add_argument("--max-fft-samples", type=int, default=2**20,
                        help="Max number of samples used for FFT (default: 2**20 about 1M)",)
    parser.add_argument("--save", action="store_true",
                        help="Save figures as .png instead of displaying them",)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    input_file = args.input_file
    
    if not os.path.isfile(input_file):
        print(f"[!] File {input_file} not found")
        sys.exit(1)
        
    prefix = os.path.splitext(os.path.basename(input_file))[0] + "_"
    
    if args.mode in ("iq", "all"):
        read_img_real(input_file, save=args.save, prefix=prefix)
        
    if args.mode in ("amplitude", "all"):
        read_amplitude(input_file, sampling_rate=args.sampling_rate, save=args.save, prefix=prefix)
    
    if args.mode in ("fft", "all"):
        read_fft(input_file, sampling_rate=args.sampling_rate, max_fft_samples=args.max_fft_samples, save=args.save, prefix=prefix)
        
    print("[OUT] Done")
