# Maintainer: thundermikey

pkgname=pid-fan-controller
pkgver=0.r22
pkgrel=1
pkgdesc="PID fan controller with Python3"
arch=('any')
url="https://github.com/ThunderMikey/pid_fan_controller"
license=('GPL3')
depends=('python3' 'python-simple-pid' 'python-pyaml')
provides=("$pkgname")
source=('pid_fan_controller.py'
        'override_auto_fan_control.py'
        'pid-fan-controller.service'
        'pid-fan-controller-sleep-hook.service'
        'pid_fan_controller_config.yaml')
md5sums=(SKIP
         SKIP
         SKIP
         SKIP
         SKIP)

backup=('etc/pid_fan_controller_config.yaml')

pkgver() {
  printf "0.r%s" "$(git rev-list --count HEAD)"
}

package() {
  echo $pkgdir
  install -m 644 -Dt "$pkgdir/usr/lib/systemd/system/" pid-fan-controller.service \
    pid-fan-controller-sleep-hook.service
  install -m 644 -Dt "$pkgdir/etc/" pid_fan_controller_config.yaml
  install -m 755 -Dt "$pkgdir/usr/share/$pkgname/" pid_fan_controller.py override_auto_fan_control.py
}

# vim:set ts=2 sw=2 et:
