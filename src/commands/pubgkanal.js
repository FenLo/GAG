const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { setPubgChannelDb } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('pubgkanal')
        .setDescription('PUBG istatistiklerinin gönderileceği kanalı ayarlar.')
        .addChannelOption(option =>
            option.setName('kanal')
                .setDescription('PUBG istatistikleri kanalı')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const channel = interaction.options.getChannel('kanal');

        setPubgChannelDb(interaction.guild.id, channel.id);

        await interaction.reply({
            content: `✅ PUBG istatistikleri artık ${channel} kanalına gönderilecek!`,
            ephemeral: true
        });
    }
};
